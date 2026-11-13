// Rasterize the flag-icons SVGs (4x3) to small PNGs with headless Chromium.
// Usage: node tools/rasterize_flags.js <flag-icons/flags/4x3 dir> <out dir>
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const [src, out] = process.argv.slice(2);
  if (!src || !out) {
    console.error('usage: node tools/rasterize_flags.js <svg dir> <out dir>');
    process.exit(1);
  }
  fs.mkdirSync(out, { recursive: true });
  const W = 320, H = 240;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  const files = fs.readdirSync(src).filter((f) => f.endsWith('.svg'));
  for (const f of files) {
    const svg = fs.readFileSync(path.join(src, f), 'utf8');
    const b64 = Buffer.from(svg).toString('base64');
    await page.setContent(
      `<html><body style="margin:0;background:#000">` +
        `<img src="data:image/svg+xml;base64,${b64}" style="width:${W}px;height:${H}px;display:block"></body></html>`
    );
    await page.waitForFunction(() => document.images[0] && document.images[0].complete);
    await page.screenshot({ path: path.join(out, f.replace('.svg', '.png')) });
  }
  await browser.close();
  console.log(`rasterized ${files.length} flags -> ${out}`);
})();
