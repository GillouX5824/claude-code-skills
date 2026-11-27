#!/usr/bin/env node
/**
 * export-pptx.js — Export an HTML slide deck to PPTX with embedded slide images.
 *
 * Each .slide element is screenshotted via Puppeteer and embedded as a full-bleed
 * image in a 16:9 PowerPoint slide.
 *
 * Usage:
 *   node export-pptx.js <input.html> [output.pptx]
 */

const puppeteer = require('puppeteer');
const pptxgen = require('pptxgenjs');
const path = require('path');
const fs = require('fs');
const os = require('os');

async function main() {
  const input = process.argv[2];
  if (!input) {
    console.error('Usage: node export-pptx.js <input.html> [output.pptx]');
    process.exit(1);
  }

  const inputPath = path.resolve(input);
  if (!fs.existsSync(inputPath)) {
    console.error(`File not found: ${inputPath}`);
    process.exit(1);
  }

  const output = process.argv[3]
    ? path.resolve(process.argv[3])
    : inputPath.replace(/\.html?$/i, '.pptx');

  console.log(`Exporting: ${path.basename(inputPath)} → ${path.basename(output)}`);

  const browser = await puppeteer.launch({ headless: 'new' });
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'slide-export-'));

  try {
    // Use a wide viewport so all slides render at full width.
    // Height is large so the full scrollable page loads without lazy-rendering.
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 5000, deviceScaleFactor: 2 });

    const fileUrl = 'file:///' + inputPath.replace(/\\/g, '/');
    await page.goto(fileUrl, { waitUntil: ['networkidle0', 'domcontentloaded'] });
    await page.evaluateHandle(() => document.fonts.ready);
    // Wait for entrance animations to complete.
    await new Promise((r) => setTimeout(r, 1200));

    // Hide the nav bar if present.
    await page.evaluate(() => {
      const nav = document.getElementById('nav');
      if (nav) nav.style.display = 'none';
    });

    const slideHandles = await page.$$('.slide');
    const slideCount = slideHandles.length;
    console.log(`Found ${slideCount} slides`);

    const imagePaths = [];

    for (let i = 0; i < slideCount; i++) {
      const imgPath = path.join(tmpDir, `slide-${String(i + 1).padStart(3, '0')}.png`);
      // elementHandle.screenshot() captures the element's bounding box directly,
      // regardless of scroll position or body padding.
      await slideHandles[i].screenshot({ path: imgPath });
      imagePaths.push(imgPath);
      process.stdout.write(`  Captured slide ${i + 1}/${slideCount}\r`);
    }

    console.log(`\nBuilding PPTX...`);

    const pptx = new pptxgen();
    // 16:9 — 13.33" × 7.5" (standard PowerPoint Widescreen)
    pptx.defineLayout({ name: 'WIDESCREEN', width: 13.33, height: 7.5 });
    pptx.layout = 'WIDESCREEN';

    for (const imgPath of imagePaths) {
      const slide = pptx.addSlide();
      slide.addImage({
        path: imgPath,
        x: 0,
        y: 0,
        w: 13.33,
        h: 7.5,
      });
    }

    await pptx.writeFile({ fileName: output });

    const kb = Math.round(fs.statSync(output).size / 1024);
    console.log(`✓ PPTX saved: ${output} (${kb} KB)`);
  } finally {
    await browser.close();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
}

main().catch((err) => {
  console.error('Error:', err.message);
  process.exit(1);
});
