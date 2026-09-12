/* Run against the local preview. HIFUN_PLAYWRIGHT can point to a bundled package. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.HIFUN_PLAYWRIGHT || 'playwright');
const origin = process.env.HIFUN_PREVIEW_URL || 'http://127.0.0.1:8765';
const output = path.resolve(__dirname, '../.preview');
fs.mkdirSync(output, { recursive: true });

(async () => {
  const browser = await chromium.launch({ channel: process.env.HIFUN_BROWSER || 'msedge', headless: true });
  const errors = [];
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    const failed = [];
    page.on('response', response => { if (response.status() >= 400) failed.push(`${response.status()} ${response.url()}`); });
    await page.goto(origin, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    assert.match(await page.locator('h1').innerText(), /HiFun/);
    assert.equal(await page.locator('.task').count(), 6);
    const loadedInitially = await page.locator('video source[src]').evaluateAll(sources => sources.map(source => source.getAttribute('src')));
    assert.deepEqual(loadedInitially, ['assets/media/hero.mp4'], 'Only the hero video loads initially');
    await page.waitForFunction(() => !document.querySelector('#hero-video').paused);
    await page.screenshot({ path: path.join(output, 'desktop.png') });

    // Validate every local URL, including assets hidden in collapsed sections.
    const links = await page.evaluate(() => [...document.querySelectorAll('[href],[src],[data-src],[poster],[data-zoom]')].flatMap(el => ['href','src','data-src','poster','data-zoom'].map(a => el.getAttribute(a)).filter(Boolean)));
    const relative = [...new Set(links.filter(url => !/^(https?:|data:|#)/.test(url)))];
    for (const url of relative) {
      const response = await context.request.head(`${origin}/${url.split('#')[0]}`);
      assert.equal(response.status(), 200, `Local resource: ${url}`);
    }
    const anchors = links.filter(url => url.startsWith('#'));
    for (const anchor of anchors) assert.equal(await page.locator(anchor).count(), 1, `Anchor ${anchor}`);
    const duplicateIds = await page.evaluate(() => { const ids = [...document.querySelectorAll('[id]')].map(e => e.id); return ids.filter((id, i) => ids.indexOf(id) !== i); });
    assert.deepEqual(duplicateIds, []);

    await page.locator('#demos').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => document.querySelector('#hero-video').paused);
    await page.locator('#demos .video-start').click();
    await page.waitForFunction(() => !document.querySelector('#demos video').paused && document.querySelector('#demos video').currentTime > .1);
    await page.locator('#method').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => document.querySelector('#demos video').paused);
    await page.locator('#demos').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => !document.querySelector('#demos video').paused);
    // Explicit user pause must survive leaving and re-entering the viewport.
    await page.locator('#demos video').evaluate(video => video.pause());
    await page.waitForTimeout(100);
    await page.locator('#method').scrollIntoViewIfNeeded();
    await page.locator('#demos').scrollIntoViewIfNeeded();
    await page.waitForTimeout(250);
    assert.equal(await page.locator('#demos video').evaluate(video => video.paused), true);

    await page.locator('#method summary').click();
    await page.locator('#method .zoom-figure').click();
    assert.equal(await page.locator('#figure-dialog').evaluate(d => d.open), true);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#figure-dialog').evaluate(d => d.open), false);
    assert.equal(await page.locator('#method .zoom-figure').evaluate(el => el === document.activeElement), true);
    await page.locator('#method summary').click();
    await context.grantPermissions(['clipboard-read', 'clipboard-write']);
    await page.locator('#copy-citation').click();
    await page.waitForFunction(() => document.querySelector('#copy-citation').textContent === 'Copied');
    assert.match(await page.evaluate(() => navigator.clipboard.readText()), /huang2026hifun/);

    // Decode each media file. These checks run sequentially to bound resource use.
    for (const source of [...new Set(links.filter(url => url.endsWith('.mp4')))]) {
      const media = await page.evaluate(async source => {
        const video = document.createElement('video');
        video.muted = true;
        const result = await new Promise((resolve, reject) => {
          const timeout = setTimeout(() => reject(new Error(`Media timeout: ${source}`)), 15000);
          video.addEventListener('loadeddata', () => {clearTimeout(timeout); resolve({width:video.videoWidth, duration:video.duration});}, {once:true});
          video.addEventListener('error', () => {clearTimeout(timeout); reject(new Error(`Media error: ${source}`));}, {once:true});
          video.src = source;
          video.load();
        });
        video.removeAttribute('src'); video.load();
        return result;
      }, source);
      assert.ok(media.width > 0 && media.duration > 0, source);
    }

    const mobile = await context.newPage();
    await mobile.setViewportSize({ width: 390, height: 844 });
    mobile.on('pageerror', e => errors.push(e.message));
    await mobile.goto(origin, {waitUntil:'networkidle'});
    await mobile.screenshot({path:path.join(output,'mobile.png')});
    await mobile.locator('.menu-toggle').click();
    assert.equal(await mobile.locator('.menu-toggle').getAttribute('aria-expanded'), 'true');
    await mobile.locator('#nav-links a[href="#results"]').click();
    assert.equal(await mobile.locator('.menu-toggle').getAttribute('aria-expanded'), 'false');
    assert.equal(await mobile.locator('.task-grid').evaluate(el => getComputedStyle(el).gridTemplateColumns.split(' ').length), 1);
    for (const selector of ['#demos','#insights','.comparison-layout','.analysis-grid','#method','#results','#training-cost','#resources']) {
      await mobile.locator(selector).scrollIntoViewIfNeeded();
      assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `Mobile overflow at ${selector}`);
    }
    await mobile.locator('.comparison-layout').screenshot({path:path.join(output,'mobile-comparison.png')});
    await mobile.locator('.analysis-grid').screenshot({path:path.join(output,'mobile-analysis.png')});
    await page.locator('.comparison-layout').screenshot({path:path.join(output,'desktop-comparison.png')});
    await page.locator('#method .method-diagram').screenshot({path:path.join(output,'desktop-method.png')});
    await page.locator('.task-grid').screenshot({path:path.join(output,'desktop-tasks.png')});
    await page.locator('.cost-layout').screenshot({path:path.join(output,'desktop-cost.png')});

    const quiet = await browser.newContext({ viewport:{width:390,height:844}, reducedMotion:'reduce' });
    const quietPage = await quiet.newPage();
    await quietPage.goto(origin,{waitUntil:'networkidle'});
    assert.equal(await quietPage.locator('video source[src]').count(),0,'Reduced motion disables unsolicited video loading');
    assert.equal(await quietPage.locator('#hero-video').evaluate(v=>v.paused),true);
    await quiet.close();
    assert.deepEqual(errors, [], 'No browser JS errors');
    assert.deepEqual(failed, [], 'No failed resource responses');
    const report = {status:'passed',localResources:relative.length,checks:['desktop and mobile layout','local resources and anchors','video decoding','lazy loading','offscreen pause and resume','explicit pause persists','mobile navigation','dialog keyboard close and focus return','clipboard','reduced-motion autoplay'],errors,failed};
    fs.writeFileSync(path.join(output,'validation.json'),JSON.stringify(report,null,2));
    console.log(JSON.stringify(report,null,2));
  } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exitCode=1;});
