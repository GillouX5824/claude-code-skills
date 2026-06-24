#!/usr/bin/env node
/**
 * export-pdf.js — Export an HTML slide deck to PDF using Puppeteer.
 *
 * Usage:
 *   node export-pdf.js <input.html> [output.pdf]
 *
 * Requirements:
 *   npm install puppeteer
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function main() {
  const input = process.argv[2];
  if (!input) {
    console.error('Usage: node export-pdf.js <input.html> [output.pdf]');
    process.exit(1);
  }

  const inputPath = path.resolve(input);
  if (!fs.existsSync(inputPath)) {
    console.error(`File not found: ${inputPath}`);
    process.exit(1);
  }

  const output = process.argv[3]
    ? path.resolve(process.argv[3])
    : inputPath.replace(/\.html?$/i, '.pdf');

  console.log(`Exporting: ${path.basename(inputPath)} → ${path.basename(output)}`);

  const browser = await puppeteer.launch({ headless: 'new' });
  try {
    const page = await browser.newPage();

    // Match the fixed 1280×720 slide dimensions used in the HTML template.
    await page.setViewport({ width: 1280, height: 720, deviceScaleFactor: 2 });

    // Build a file:// URL that works on both Windows and Unix.
    const fileUrl = 'file:///' + inputPath.replace(/\\/g, '/');
    await page.goto(fileUrl, { waitUntil: ['networkidle0', 'domcontentloaded'] });

    // Wait for web fonts (DM Serif Display, Manrope) to finish loading.
    await page.evaluateHandle(() => document.fonts.ready);

    // Brief pause so any entrance animations have finished.
    await new Promise((r) => setTimeout(r, 600));

    // page.pdf() automatically switches to @media print, which our CSS uses to
    // show all slides stacked vertically with page-break-after: always.
    await page.pdf({
      path: output,
      width: '1280px',   // 16:9 — matches PowerPoint Widescreen (13.33" × 7.5")
      height: '720px',
      printBackground: true,
      preferCSSPageSize: false,
      margin: { top: '0', right: '0', bottom: '0', left: '0' },
    });

    const kb = Math.round(fs.statSync(output).size / 1024);
    console.log(`✓ PDF saved: ${output} (${kb} KB)`);
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error('Error:', err.message);
  if (err.message.includes("Cannot find module 'puppeteer'")) {
    console.error('\nInstall puppeteer first: npm install puppeteer');
  }
  process.exit(1);
});
