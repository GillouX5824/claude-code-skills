#!/usr/bin/env python3
"""Save / restore the Claude Code terminals running in a VS Code project folder.

  list    show the live Claude sessions in the project
  save    record them, then close that project's VS Code window
  restore reopen the project in VS Code with one named terminal per saved session

Works on Windows and macOS. Standard library only.
Usage: claude_vscode_sessions.py {list|save|restore} [--project PATH] [options]
"""
import argparse, json, os, re, shutil, signal, subprocess, sys, time
from pathlib import Path

IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
CLAUDE_DIR = Path.home() / ".claude"
REGISTRY = CLAUDE_DIR / "sessions"
STATE_DIR = CLAUDE_DIR / "vscode-sessions"
# Per-session variables Claude Code injects into its child processes (not user configuration)
CHILD_ENV = re.compile(r"^(CLAUDECODE|CLAUDE_PID|CLAUDE_CODE_ENTRYPOINT|"
                       r"CLAUDE_CODE_(CHILD|SESSION|MESSAGING)_\w*)$", re.I)


def norm(p):
    p = os.path.realpath(str(p)).rstrip("\\/")
    return p.lower() if (IS_WIN or IS_MAC) else p  # both default to case-insensitive filesystems


def state_file(project):
    key = re.sub(r"[^A-Za-z0-9._-]+", "_", norm(project)).strip("_")
    return STATE_DIR / f"{key[-150:]}.json"


# ---------- processes ----------
def process_table():
    """[(pid, ppid, command_line)] for every process."""
    if IS_WIN:
        ps = ("Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,CommandLine"
              " | ConvertTo-Json -Compress")
        out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                             capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
        rows = json.loads(out or "[]")
        return [(r["ProcessId"], r["ParentProcessId"], r.get("CommandLine") or "") for r in rows]
    out = subprocess.run(["ps", "-axo", "pid=,ppid=,command="], capture_output=True, text=True).stdout
    rows = []
    for line in out.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) >= 2:
            rows.append((int(parts[0]), int(parts[1]), parts[2] if len(parts) > 2 else ""))
    return rows


def ancestors(table):
    parent = {pid: ppid for pid, ppid, _ in table}
    out, pid = set(), os.getpid()
    while pid in parent and pid not in out and pid > 1:
        out.add(pid)
        pid = parent[pid]
    return out


def kill(pid):
    try:
        if IS_WIN:
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
        else:
            os.kill(pid, signal.SIGTERM)
    except OSError:
        pass


# ---------- sessions ----------
def live_sessions(project, table):
    alive = {pid for pid, _, _ in table}
    target, found = norm(project), []
    for f in REGISTRY.glob("*.json"):
        try:
            s = json.loads(f.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
        if s.get("kind") == "interactive" and s.get("pid") in alive and norm(s.get("cwd", "")) == target:
            found.append(s)
    found.sort(key=lambda s: s.get("startedAt", 0))

    # A restored session that is still on a startup prompt hasn't registered yet; find it from
    # the previous manifest by its command line so it isn't silently dropped.
    sf, seen = state_file(project), {s["pid"] for s in found}
    if sf.exists():
        try:
            prev = json.loads(sf.read_text(encoding="utf-8-sig")).get("sessions", [])
        except (OSError, ValueError):
            prev = []
        for e in prev:
            for pid, _, cmd in table:
                if pid not in seen and f"--resume {e['sessionId']}" in cmd and e["name"] in cmd:
                    found.append({"name": e["name"], "sessionId": e["sessionId"], "pid": pid,
                                  "status": "start"})
                    seen.add(pid)
    return found


def print_sessions(sessions):
    for s in sessions:
        print(f"  {s['name']:<32} {s.get('status', '?'):<6} {s['sessionId']}  (pid {s['pid']})")
    ids = [s["sessionId"] for s in sessions]
    for sid in sorted({i for i in ids if ids.count(i) > 1}):
        names = ", ".join(s["name"] for s in sessions if s["sessionId"] == sid)
        print(f"WARNING: session {sid} is shared by {ids.count(sid)} terminals ({names}); "
              "they will be restored as separate forks.")


# ---------- closing the VS Code window ----------
def close_window_windows(folder):
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    found = []
    proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            t = ctypes.create_unicode_buffer(512); user32.GetWindowTextW(hwnd, t, 512)
            c = ctypes.create_unicode_buffer(256); user32.GetClassNameW(hwnd, c, 256)
            if c.value == "Chrome_WidgetWin_1" and folder in t.value and "Visual Studio Code" in t.value:
                found.append(hwnd)
        return True

    user32.EnumWindows(proc(cb), 0)
    for h in found:
        user32.PostMessageW(h, 0x0010, 0, 0)  # WM_CLOSE, same as clicking X
    return len(found)


def close_window_mac(folder, quit_app):
    folder_as = folder.replace("\\", "\\\\").replace('"', '\\"')
    script = f'''
tell application "System Events"
  if not (exists process "Code") then return 0
  tell process "Code"
    set ws to (every window whose name contains "{folder_as}")
    repeat with w in ws
      click (first button of w whose subrole is "AXCloseButton")
    end repeat
    return count of ws
  end tell
end tell'''
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if r.returncode == 0:
        return int((r.stdout.strip() or "0"))
    print("Could not close the window via System Events:", r.stderr.strip())
    print("Grant Accessibility access to your terminal app (System Settings > Privacy & Security > "
          "Accessibility), or re-run with --quit-app to quit VS Code entirely.")
    if quit_app:
        subprocess.run(["osascript", "-e", 'quit app "Visual Studio Code"'])
        return 1
    return 0


# ---------- commands ----------
def cmd_list(a):
    sessions = live_sessions(a.project, process_table())
    print(f"Live Claude sessions in {a.project}: {len(sessions)}")
    print_sessions(sessions)


def cmd_save(a):
    if a.detach:
        return detach(a)
    self_pids = set(map(int, a.self_pids.split(","))) if a.self_pids else ancestors(process_table())

    # 1. wait until nothing is mid-turn (the session running this script doesn't count)
    deadline = time.time() + a.busy_wait * 60
    while True:
        table = process_table()
        sessions = live_sessions(a.project, table)
        busy = [s["name"] for s in sessions if s.get("status") == "busy" and s["pid"] not in self_pids]
        if not busy:
            break
        if time.time() > deadline:
            sys.exit(f"Still busy after {a.busy_wait} min: {', '.join(busy)}. Nothing closed.")
        print("Waiting for busy session(s):", ", ".join(busy), flush=True)
        time.sleep(10)
    if not sessions:
        sys.exit(f"No live Claude sessions found in {a.project}")

    # 2. manifest (transcripts are already on disk; this records which ones were open)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    sf = state_file(a.project)
    entries = [{"name": s["name"], "sessionId": s["sessionId"], "pid": s["pid"]} for s in sessions]
    sf.write_text(json.dumps({"project": a.project, "savedAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
                              "sessions": entries}, indent=2), encoding="utf-8")
    print(f"Saved {len(entries)} session(s) to {sf}")
    print_sessions(sessions)
    if a.no_close:
        return

    # 3. close only this project's VS Code window
    folder = os.path.basename(a.project)
    n = close_window_windows(folder) if IS_WIN else close_window_mac(folder, a.quit_app) if IS_MAC else 0
    if not n:
        sys.exit(f"No VS Code window for '{folder}' was closed; sessions left running.")
    print(f"Closing VS Code window for {folder} ...", flush=True)

    # 4. make sure the claude processes are gone (they're idle, so stopping them is safe)
    pids = {e["pid"] for e in entries}
    for _ in range(30):
        if not pids & {p for p, _, _ in process_table()}:
            break
        time.sleep(1)
    left = pids & {p for p, _, _ in process_table()}
    for pid in left:
        kill(pid)
    if left:
        print(f"Stopped {len(left)} leftover claude process(es).")
    print(f'Done. Restore with: restore --project "{a.project}"')


def detach(a):
    """Re-launch save in a process that survives the VS Code window (and this terminal) closing."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    log = STATE_DIR / "last-save.log"
    argv = [sys.executable, "-u", os.path.abspath(__file__), "save", "--project", a.project,
            "--busy-wait", str(a.busy_wait), "--self-pids", ",".join(map(str, ancestors(process_table())))]
    if a.no_close: argv.append("--no-close")
    if a.quit_app: argv.append("--quit-app")
    out = open(log, "w", encoding="utf-8")
    kw = dict(stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, cwd=str(Path.home()))
    if IS_WIN:
        base = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        try:
            subprocess.Popen(argv, creationflags=base | 0x01000000, **kw)  # + CREATE_BREAKAWAY_FROM_JOB
        except OSError:
            subprocess.Popen(argv, creationflags=base, **kw)
    else:
        subprocess.Popen(argv, start_new_session=True, **kw)
    print(f"Save running in the background; log: {log}")


def cmd_restore(a):
    sf = state_file(a.project)
    if not sf.exists():
        sys.exit(f"No saved state for {a.project} (expected {sf}). Run save first.")
    state = json.loads(sf.read_text(encoding="utf-8-sig"))
    sessions = state["sessions"]
    claude = shutil.which("claude") or str(Path.home() / ".local" / "bin" / "claude")
    ids = [s["sessionId"] for s in sessions]

    tasks = []
    for s in sessions:
        args = ["--resume", s["sessionId"], "--name", s["name"]]
        if ids.count(s["sessionId"]) > 1:
            args.append("--fork-session")  # shared session: give each terminal its own id from now on
        tasks.append({
            "label": f"claude: {s['name']}", "type": "process", "command": claude, "args": args,
            "options": {"cwd": "${workspaceFolder}"}, "isBackground": True, "problemMatcher": [],
            "presentation": {"panel": "dedicated", "reveal": "always", "focus": False, "echo": False},
            "runOptions": {"runOn": "folderOpen"},
        })

    vdir = Path(a.project) / ".vscode"
    tfile, backup = vdir / "tasks.json", vdir / "tasks.json.claude-restore.bak"
    created_dir = not vdir.exists()
    vdir.mkdir(exist_ok=True)
    if tfile.exists():
        shutil.copy2(tfile, backup)
    tfile.write_text(json.dumps({"version": "2.0.0", "tasks": tasks}, indent=2), encoding="utf-8")

    print(f"Opening {a.project} with {len(sessions)} Claude terminal(s): "
          + ", ".join(s["name"] for s in sessions))
    print("If VS Code asks to allow automatic tasks for this folder, click Allow.", flush=True)
    # When this runs inside a Claude Code session, the variables Claude sets for its child processes
    # (e.g. CLAUDE_CODE_CHILD_SESSION=1) would flow into the new VS Code window and from there into
    # the resumed sessions, which would then treat themselves as children and turn transcript saving off.
    env = {k: v for k, v in os.environ.items() if not CHILD_ENV.match(k)}
    code = shutil.which("code")
    if code:
        subprocess.Popen([code, a.project], env=env)
    elif IS_MAC:
        subprocess.Popen(["open", "-a", "Visual Studio Code", a.project], env=env)
    else:
        sys.exit("'code' command not found on PATH.")

    # wait for each session to be relaunched, then remove the temporary tasks.json
    deadline, started = time.time() + a.wait, 0
    while time.time() < deadline:
        cmds = [c for _, _, c in process_table() if "--resume" in c]
        started = sum(any(s["sessionId"] in c and s["name"] in c for c in cmds) for s in sessions)
        if started >= len(sessions):
            break
        time.sleep(3)

    if started >= len(sessions):
        tfile.unlink()
        if backup.exists():
            backup.replace(tfile)
        elif created_dir and not any(vdir.iterdir()):
            vdir.rmdir()
        print(f"All {started} session(s) resumed. Temporary tasks.json removed.")
    else:
        print(f"WARNING: only {started} of {len(sessions)} sessions started within {a.wait}s. "
              f"{tfile} left in place: run 'Tasks: Run Task' > 'claude: <name>' for the missing ones, "
              "then delete it (it would otherwise run again on every open).")
        sys.exit(1)


def known_projects():
    """{normalized path: (path, 'running'/'saved'/'running+saved')} from live sessions and saved state."""
    found = {}
    alive = {pid for pid, _, _ in process_table()}
    for f in REGISTRY.glob("*.json"):
        try:
            s = json.loads(f.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
        if s.get("kind") == "interactive" and s.get("pid") in alive and s.get("cwd"):
            found[norm(s["cwd"])] = (s["cwd"].rstrip("\\/"), "running")
    for f in STATE_DIR.glob("*.json"):
        try:
            proj = json.loads(f.read_text(encoding="utf-8-sig")).get("project")
        except (OSError, ValueError):
            continue
        if proj:
            k = norm(proj)
            found[k] = (found[k][0], "running+saved") if k in found else (proj, "saved")
    return found


def resolve_project(arg):
    """A path is used as-is; otherwise treat it as a folder name and look it up."""
    path = os.path.realpath(os.path.expanduser(arg)).rstrip("\\/")
    if os.path.isdir(path):
        return path
    name = arg.strip().strip("\\/").lower()
    projects = known_projects().values()
    matches = [p for p in projects if os.path.basename(p[0]).lower() == name]
    if not matches:  # fall back to a partial name match
        matches = [p for p in projects if name in os.path.basename(p[0]).lower()]
    if len(matches) == 1:
        print(f"Project '{arg}' -> {matches[0][0]}")
        return os.path.realpath(matches[0][0]).rstrip("\\/")
    if matches:
        print(f"'{arg}' matches several projects; pass the full path with --project:")
        for path_, src in sorted(matches):
            print(f"  [{src}] {path_}")
        sys.exit(2)
    print(f"No folder or known project called '{arg}'. Known projects:")
    for path_, src in sorted(projects):
        print(f"  [{src}] {path_}")
    sys.exit(2)


def cmd_projects(_):
    projects = sorted(known_projects().values())
    print(f"Known projects: {len(projects)}")
    for path_, src in projects:
        print(f"  [{src}] {path_}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["projects", "list", "save", "restore"])
    p.add_argument("--project", default=os.getcwd(),
                   help="project folder path, or just its name (default: current directory)")
    p.add_argument("--busy-wait", type=int, default=10, help="save: minutes to wait for busy sessions")
    p.add_argument("--detach", action="store_true",
                   help="save: run in the background (needed when called from a session inside the project)")
    p.add_argument("--no-close", action="store_true", help="save: only record, don't close VS Code")
    p.add_argument("--quit-app", action="store_true", help="save (macOS): quit VS Code if a window can't be closed")
    p.add_argument("--wait", type=int, default=180, help="restore: seconds to wait for sessions to start")
    p.add_argument("--self-pids", help=argparse.SUPPRESS)
    a = p.parse_args()
    if a.command == "projects":
        return cmd_projects(a)
    a.project = resolve_project(a.project)
    {"list": cmd_list, "save": cmd_save, "restore": cmd_restore}[a.command](a)


if __name__ == "__main__":
    main()
