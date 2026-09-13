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
    assert.deepEqual(loadedInitially, [], 'No video body loads on initial entry');
    assert.equal(await page.locator('h1').evaluate(el => getComputedStyle(el).fontSize), '42px');
    assert.deepEqual(await page.locator('.brand').allTextContents(), ['HiFun', 'HiFun']);
    assert.equal(await page.locator('.wordmark').innerText(), 'HiFun');
    assert.deepEqual(await page.locator('#nav-links a').allTextContents(), ['Overview','Challenges','Demos','Evidence','Method','Results','Resources']);
    assert.deepEqual(await page.locator('main > section').evaluateAll(els => els.map(el => el.id)), ['top','overview','abstract','challenges','highlights','demos','insights','method','results','training-cost','resources']);
    assert.equal(await page.locator('#full-video').count(), 1);
    assert.equal(await page.locator('#overview h2').innerText(), 'Overview');
    assert.equal(await page.locator('#overview .eyebrow').count(),0);
    assert.equal((await page.locator('#full-video .video-start').innerText()).replace('▶','').trim(),'Play video');
    assert.equal(await page.locator('#full-video .video-start').getAttribute('aria-label'),'Play overview video');
    assert.equal(await page.locator('.resource-buttons a[href="#full-video"]').innerText(),'Overview video ↗');
    assert.doesNotMatch(await page.locator('#overview').innerText(),/supplementary/i);
    const abstractStyles = target => target.locator('#abstract .abstract p:not(.source-note)').evaluateAll(els => els.map(el => { const s=getComputedStyle(el); return [s.textAlign,s.textAlignLast,s.hyphens]; }));
    assert.deepEqual(await abstractStyles(page), [['justify','left','auto'],['justify','left','auto']]);
    assert.equal(await page.locator('#abstract .source-note').count(),0);
    assert.doesNotMatch(await page.locator('#abstract').innerText(),/Abstract from the supplied manuscript/);
    assert.equal(await page.locator('#demos h2').innerText(),'Precise contact · Arm–hand coordination · Reactive recovery');
    assert.match(await page.locator('#demos .section-heading').innerText(),/slipping, trapping the tool, or colliding/);
    assert.equal(await page.locator('#demos h2 br').count(),0);
    assert.equal(await page.locator('#demos h2').evaluate(el=>el.getBoundingClientRect().height <= parseFloat(getComputedStyle(el).lineHeight)+1),true,'Desktop task title fits one line');
    assert.equal(await page.locator('#demos .section-heading > p:last-child').evaluate(el=>Math.abs(el.getBoundingClientRect().width-el.closest('.container').getBoundingClientRect().width)<1),true,'Task introduction spans the content width');
    const readingSelectors=['[data-kind="iaw"] figcaption','[data-kind="iaw"] figcaption strong','.source-note','.evidence-link','.contact-sequence p','.resource-list small','.paired-numbers p'];
    for(const selector of readingSelectors) assert.equal(await page.locator(selector).first().evaluate(el=>getComputedStyle(el).fontSize),'17px',selector);

    assert.doesNotMatch(await page.locator('[data-kind="skill"] figcaption').innerText(),/Source timing preserved|outside the six-task/);
    assert.equal(await page.locator('.comparison-clips source').nth(1).getAttribute('data-src'),'assets/media/intervention-hifun.mp4');
    assert.match(await page.locator('[data-kind="intervention"] figcaption').innerText(),/This avoids direct full-DoF arm-hand exploration and enables more efficient real-world learning/);
    assert.match(await page.locator('[data-kind="iaw"] figcaption').innerText(),/in the same state/);
    assert.doesNotMatch(await page.locator('[data-kind="iaw"] figcaption').innerText(),/not a direct measurement/);
    assert.deepEqual(await page.locator('.challenge-media').evaluateAll(els=>els.map(el=>el.dataset.kind)),['skill','critic','intervention','iaw']);
    assert.equal(await page.locator('#challenges .zoom-figure').count(),4);
    assert.equal(await page.locator('.interface-flow').count(),0);
    assert.equal(await page.locator('.intervention-comparison video').count(),2);
    assert.equal(await page.locator('.critic-method img').getAttribute('src'),'assets/figures/method-critic.webp');
    assert.equal(await page.locator('.iaw-method img').getAttribute('src'),'assets/figures/method-iaw.webp');
    assert.equal(await page.locator('[data-kind="iaw"] .challenge-plots').count(),0);
    assert.deepEqual(await page.locator('.comparison-clip-heading h5').allTextContents(),['Full-DoF HIL-SERL','HiFun']);
    assert.equal(await page.locator('#abstract').count(), 1);
    assert.equal(await page.locator('#abstract details').count(), 0);
    assert.equal(await page.locator('.challenge-row').count(), 4);
    assert.equal(await page.getByText('Baseline comparison and evaluation protocol', {exact:true}).count(), 0);
    assert.equal(await page.locator('#insights h2').innerText(), 'Evidence behind the design');
    assert.deepEqual(await page.locator('.bar-row > strong').allTextContents(), ['12.5%','46%','100%']);
    await page.screenshot({ path: path.join(output, 'desktop.png') });
    await page.locator('#full-video .video-start').click();
    await page.waitForFunction(() => !document.querySelector('#full-video video').paused);
    assert.deepEqual(await page.locator('video source[src]').evaluateAll(els => els.map(el => el.getAttribute('src'))), ['assets/media/supplementary.mp4']);
    await page.locator('#hero-video').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => { const v=document.querySelector('#hero-video'); return !v.paused && v.readyState >= 2; });
    await page.waitForFunction(() => document.querySelector('#full-video video').paused);
    assert.equal(await page.locator('#hero-video').evaluate(v => v.duration), 25);
    await page.locator('#hero-video').evaluate(v => v.pause());
    for (const [time, caption] of [[6.9,'Contact, leverage, retrieve'],[7,'Align the tool, actuate the trigger'],[17.9,'Align the tool, actuate the trigger'],[18,'Lose contact, adapt, recover']]) {
      await page.locator('#hero-video').evaluate(async (v, time) => {v.currentTime = time; await new Promise(resolve => v.addEventListener('seeked',resolve,{once:true}));}, time);
      // Remote media can deliver timeupdate after seeked; wait for the rendered caption.
      await page.waitForFunction(caption => document.querySelector('#hero-scene').textContent === caption, caption);
      assert.equal(await page.locator('#hero-scene').innerText(), caption);
    }
    await page.locator('[data-kind="skill"] video').scrollIntoViewIfNeeded();
    assert.equal(await page.locator('[data-kind="skill"] video source[src]').count(),0,'Skill clip waits for a click even when visible');
    await page.locator('[data-kind="skill"] .video-start').click();
    await page.waitForFunction(()=>document.querySelector('[data-kind="skill"] video').currentTime>.1);
    assert.ok(Math.abs(await page.locator('[data-kind="skill"] video').evaluate(v=>v.duration)-25.17)<.05);
    await page.locator('#method').scrollIntoViewIfNeeded();
    await page.waitForFunction(()=>document.querySelector('[data-kind="skill"] video').paused);
    await page.locator('.intervention-comparison').scrollIntoViewIfNeeded();
    assert.equal(await page.locator('.intervention-comparison video source[src]').count(),0,'Comparison waits for user playback');
    await page.locator('.play-comparison').click();
    await page.waitForFunction(()=>[...document.querySelectorAll('.intervention-comparison video')].every(v=>!v.paused && v.currentTime>.1));
    const comparisonDurations=await page.locator('.intervention-comparison video').evaluateAll(videos=>videos.map(v=>v.duration));
    assert.ok(Math.abs(comparisonDurations[0]-7)<.05 && Math.abs(comparisonDurations[1]-7.03)<.05);
    assert.deepEqual(await page.locator('.intervention-comparison video').evaluateAll(videos=>videos.map(v=>[v.loop,v.playbackRate])),[[true,1],[true,1]]);
    await page.locator('.play-comparison').click();
    assert.equal(await page.locator('.intervention-comparison video').evaluateAll(videos=>videos.every(v=>v.paused)),true);
    await page.locator('.play-comparison').click();
    await page.locator('#method').scrollIntoViewIfNeeded();
    await page.waitForFunction(()=>[...document.querySelectorAll('.intervention-comparison video')].every(v=>v.paused));
    for (const button of await page.locator('#challenges .zoom-figure').all()) {
      await button.click();
      assert.equal(await page.locator('#figure-dialog').evaluate(d=>d.open),true);
      assert.equal(await page.locator('#enlarged-figure').getAttribute('src'),await button.getAttribute('data-zoom'));
      await page.keyboard.press('Escape');
      assert.equal(await button.evaluate(el=>el===document.activeElement),true);
    }
    for (const media of await page.locator('.challenge-media').all()) {
      await media.scrollIntoViewIfNeeded();
      await media.evaluate(async el=>{await Promise.all([...el.querySelectorAll('img')].map(img=>img.decode()));});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
      await media.screenshot({path:path.join(output,`desktop-challenge-${await media.getAttribute('data-kind')}.png`),style:'.site-header,.skip-link{visibility:hidden!important}'});
    }
    await page.locator('#abstract').screenshot({path:path.join(output,'desktop-abstract.png')});
    await page.locator('#highlights').screenshot({path:path.join(output,'desktop-highlights.png')});
    await page.locator('.recovery-sequence').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => document.querySelector('.recovery-sequence img').naturalWidth === 7421);
    assert.equal(await page.locator('.recovery-sequence').evaluate(el => el.previousElementSibling.classList.contains('wide-evidence')), true);
    await page.locator('.recovery-sequence').screenshot({path:path.join(output,'desktop-recovery.png')});
    await page.locator('.recovery-sequence .zoom-figure').click();
    assert.equal(await page.locator('#figure-dialog').evaluate(d => d.open), true);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#figure-dialog').evaluate(d => d.open), false);

    // Validate every local URL, including assets hidden in collapsed sections.
    const links = await page.evaluate(() => [...document.querySelectorAll('[href],[src],[data-src],[poster],[data-zoom]')].flatMap(el => ['href','src','data-src','poster','data-zoom'].map(a => el.getAttribute(a)).filter(Boolean)));
    const relative = [...new Set(links.filter(url => !/^(https?:|data:|blob:|#)/.test(url)))];
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
    assert.equal(await page.locator('.training-stages li').count(),3);
    assert.deepEqual(await page.locator('.training-stages strong').evaluateAll(els => els.map(el => getComputedStyle(el).display)), ['block','block','block']);
    await page.locator('.training-stages').screenshot({path:path.join(output,'desktop-training-stages.png')});
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
    await mobile.evaluate(() => document.fonts.ready);
    assert.equal(await mobile.locator('h1').evaluate(el => getComputedStyle(el).fontSize), '26px');
    for(const selector of readingSelectors) assert.equal(await mobile.locator(selector).first().evaluate(el=>getComputedStyle(el).fontSize),'16px',selector);
    assert.equal(await mobile.locator('#demos .section-heading > p:last-child').evaluate(el=>Math.abs(el.getBoundingClientRect().width-el.closest('.container').getBoundingClientRect().width)<1),true);

    assert.equal(await mobile.locator('video source[src]').count(),0);
    assert.deepEqual(await abstractStyles(mobile), [['justify','left','auto'],['justify','left','auto']]);
    for (const media of await mobile.locator('.challenge-media').all()) {
      await media.scrollIntoViewIfNeeded();
      await media.evaluate(async el=>{await Promise.all([...el.querySelectorAll('img')].map(img=>img.decode()));});
      assert.equal(await mobile.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
      for(const grid of await media.locator('.critic-design-evidence,.comparison-clips').all()) assert.equal(await grid.evaluate(el=>getComputedStyle(el).gridTemplateColumns.split(' ').length),1);
      const plots=media.locator('.challenge-plots');
      if(await plots.count()) assert.equal(await plots.evaluate(el=>getComputedStyle(el).gridTemplateColumns.split(' ').length),1);
      await media.screenshot({path:path.join(output,`mobile-challenge-${await media.getAttribute('data-kind')}.png`),style:'.site-header,.skip-link{visibility:hidden!important}'});
    }
    await mobile.locator('.challenge-plots .zoom-figure').first().focus();
    await mobile.keyboard.press('Enter');
    assert.equal(await mobile.locator('#figure-dialog').evaluate(d=>d.open),true);
    await mobile.keyboard.press('Escape');
    assert.equal(await mobile.locator('.challenge-plots .zoom-figure').first().evaluate(el=>el===document.activeElement),true);
    await mobile.locator('#top').evaluate(el=>el.scrollIntoView({behavior:'instant'}));
    await mobile.screenshot({path:path.join(output,'mobile.png')});
    await mobile.locator('.challenge-row').first().screenshot({path:path.join(output,'mobile-challenge.png')});
    assert.equal(await mobile.locator('.challenge-row').first().evaluate(el => getComputedStyle(el).gridTemplateColumns.split(' ').length),1);
    await mobile.locator('.recovery-scroll').scrollIntoViewIfNeeded();
    await mobile.waitForFunction(() => document.querySelector('.recovery-sequence img').naturalWidth === 7421);
    assert.equal(await mobile.locator('.recovery-scroll').evaluate(el => el.scrollWidth > el.clientWidth),true);
    await mobile.locator('.recovery-scroll').focus();
    await mobile.keyboard.press('ArrowRight');
    await mobile.waitForFunction(() => document.querySelector('.recovery-scroll').scrollLeft > 0);
    await mobile.locator('.recovery-scroll').evaluate(el => el.scrollLeft=0);
    await mobile.locator('.recovery-sequence').screenshot({path:path.join(output,'mobile-recovery.png')});
    await mobile.locator('.recovery-scroll .zoom-figure').focus();
    await mobile.keyboard.press('Enter');
    assert.equal(await mobile.locator('#figure-dialog').evaluate(d => d.open),true);
    assert.equal(await mobile.locator('.dialog-image-scroll').evaluate(el => el.scrollWidth > el.clientWidth),true);
    await mobile.keyboard.press('Escape');
    assert.equal(await mobile.locator('#figure-dialog').evaluate(d => d.open),false);
    await mobile.locator('.menu-toggle').click();
    assert.equal(await mobile.locator('.menu-toggle').getAttribute('aria-expanded'), 'true');
    await mobile.locator('#nav-links a[href="#results"]').click();
    assert.equal(await mobile.locator('.menu-toggle').getAttribute('aria-expanded'), 'false');
    assert.equal(await mobile.locator('.task-grid').first().evaluate(el => getComputedStyle(el).gridTemplateColumns.split(' ').length), 1);
    for (const selector of ['#top','#overview','#abstract','#challenges','#highlights','.recovery-sequence','#demos','#insights','.comparison-layout','.analysis-grid','#method','#results','#training-cost','#resources']) {
      await mobile.locator(selector).scrollIntoViewIfNeeded();
      assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `Mobile overflow at ${selector}`);
    }
    await mobile.locator('.comparison-layout').screenshot({path:path.join(output,'mobile-comparison.png')});
    await mobile.locator('.analysis-grid').screenshot({path:path.join(output,'mobile-analysis.png')});
    await page.locator('.comparison-layout').screenshot({path:path.join(output,'desktop-comparison.png')});
    await page.locator('#method .method-diagram').screenshot({path:path.join(output,'desktop-method.png')});
    await page.locator('.task-grid').first().screenshot({path:path.join(output,'desktop-tasks.png')});
    await page.locator('.cost-layout').screenshot({path:path.join(output,'desktop-cost.png')});

    const quiet = await browser.newContext({ viewport:{width:390,height:844}, reducedMotion:'reduce' });
    const quietPage = await quiet.newPage();
    await quietPage.goto(origin,{waitUntil:'networkidle'});
    await quietPage.locator('#hero-video').scrollIntoViewIfNeeded();
    await quietPage.waitForTimeout(300);
    assert.equal(await quietPage.locator('video source[src]').count(),0,'Reduced motion disables unsolicited video loading');
    assert.equal(await quietPage.locator('#hero-video').evaluate(v=>v.paused),true);
    await quiet.close();
    assert.deepEqual(errors, [], 'No browser JS errors');
    assert.deepEqual(failed, [], 'No failed resource responses');
    const report = {status:'passed',localResources:relative.length,checks:['full-width task introduction and single-line desktop title','17px desktop and 16px mobile captions and supporting copy','paper-grounded task challenges and IAW explanation','removed abstract attribution and requested clip notes','Overview naming and accessible play button','justified desktop/mobile Abstract with left-aligned final lines','four matching challenge media and responsive subplots','full author-selected skill video','method modules and experimental plot keyboard zoom','Full-DoF HIL-SERL versus HiFun video, shared playback and source speeds','v2 narrative order and nonduplicated overview','42px desktop and 26px mobile title','four challenge-insight relationships','25-second highlights and exact 7s/18s caption boundaries','five-frame image and keyboard-accessible mobile scrolling','method step title line breaks','desktop and mobile layout','local resources and anchors','video decoding','lazy loading','offscreen pause and resume','explicit pause persists','mobile navigation','dialog keyboard close and focus return','clipboard','reduced-motion autoplay'],errors,failed};
    fs.writeFileSync(path.join(output,'validation.json'),JSON.stringify(report,null,2));
    console.log(JSON.stringify(report,null,2));
  } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exitCode=1;});
