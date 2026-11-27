---
name: vscode-claude-sessions
description: Save and restore the Claude Code terminals open in a VS Code project. "Save" records every live Claude session in the folder and closes that VS Code window. "Restore" reopens the folder and resumes each session in its own named terminal. Works on Windows and macOS. Use whenever the user wants to close VS Code without losing their Claude terminals, park or suspend a project, reboot or shut down and come back later, snapshot their open sessions, or reopen a project "with all my Claude sessions". Also use when they ask which Claude sessions are running in a folder.
---

# VS Code Claude sessions: save / restore

Everything is done by `scripts/claude_vscode_sessions.py`, which uses only the Python standard library. Run it with
`python` on Windows and `python3` on macOS. On Windows, `python3` is often just the Microsoft Store stub.

```
<python> <skill-dir>/scripts/claude_vscode_sessions.py projects
<python> <skill-dir>/scripts/claude_vscode_sessions.py list    --project "<path or name>"
<python> <skill-dir>/scripts/claude_vscode_sessions.py save    --project "<path or name>" [--detach]
<python> <skill-dir>/scripts/claude_vscode_sessions.py restore --project "<path or name>"
```

`--project` accepts a full path or just the folder name the user said (e.g. `client-operations-platform`), so
pass their words straight through. Don't search the disk yourself. A name is looked up among the working folders
of the Claude sessions running now and among previously saved projects. An exact folder-name match wins over a
partial one. The script prints the folder it resolved to; mention it to the user. If the name matches several
projects, or none, the script exits with code 2 and prints the candidates. In that case ask the user which one
they mean, or ask for the full path, then re-run with the full path. `projects` lists everything it knows.
With no `--project` it uses the current directory, so always pass it so the window being closed is unambiguous.
Sessions are matched exactly against their working directory, so ones started in a subfolder are not included.

## How it works (so you can explain or debug it)

- Each running Claude Code process writes `~/.claude/sessions/<pid>.json` with its `cwd`, `sessionId`, `name`
  and `status` (idle/busy). **save** reads these, waits until none of them is `busy` (closing mid-turn would lose
  the answer), and writes the list to `~/.claude/vscode-sessions/<path-key>.json`. Conversations are already
  persisted continuously, so the manifest is the only thing that needs saving.
- It then closes only the VS Code window whose title contains the folder name. On Windows it sends WM_CLOSE. On
  macOS it clicks the window's close button through System Events, which needs Accessibility permission for the
  terminal app. `--quit-app` quits VS Code entirely as a fallback. Any claude process still alive after 30s is
  stopped.
- **restore** writes a temporary `.vscode/tasks.json` with one `runOn: folderOpen` task per session, each running
  `claude --resume <sessionId> --name <name>`. It opens the folder with `code`, waits until every session's
  process has appeared, then deletes the tasks file (restoring any tasks.json that was there before).
  It resumes by **session id, not name**, because names are not unique.

## Workflow

### Save
1. Run `list` and show the user what will be saved. If it warns that a session is shared by several terminals,
   explain it. This happens when several terminals were started with `claude --continue`, which picks up the
   same most recent conversation, so they all write into one file. Restore gives each its own fork via
   `--fork-session`, but each fork starts with the mixed history.
2. Confirm before running `save`, because it closes a VS Code window and ends the sessions in it.
3. Check whether *this* session's working directory is the project folder. If it is, closing the window
   kills this session too, so run `save` with `--detach`. That lets the script survive and finish in the
   background, and its output goes to `~/.claude/vscode-sessions/last-save.log`. Tell the user before running it
   that this conversation will end and how to restore. The busy-wait automatically ignores the session that
   launched the script.
4. Report what was saved and the restore command.

### Restore
1. Run `restore`. It can be run from any terminal or any Claude session.
2. On the first run in a folder, VS Code may ask to allow automatic tasks: tell the user to click Allow.
3. If it reports that not all sessions started, a resumed session may be waiting on a prompt. For example,
   a large conversation can ask whether to resume from a summary. Ask the user to look at the terminals.
   `tasks.json` is left in place in that case and should be deleted afterwards, or it will run on every open.

## Running it without Claude
The user can run the same commands directly in a terminal. On macOS the `code` command must be installed via
VS Code's "Shell Command: Install 'code' command in PATH". Without it, restore falls back to `open -a "Visual Studio Code"`.
