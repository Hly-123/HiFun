"""Build the fully static research page. Python standard library only."""
from pathlib import Path
from html import escape
import hashlib

ROOT = Path(__file__).resolve().parents[1]


def film(name, label, *, autoplay=False, speed='', portrait=False, loop=True, button_label=None, hold_last_frame=False):
    return f'''<div class="media-frame{' portrait-video' if portrait else ''}">
      <video class="managed-video" {'id="hero-video"' if autoplay else ''} {'controls' if name == 'supplementary' else 'data-autoplay data-simple-player controlslist="nodownload noplaybackrate noremoteplayback" disablepictureinpicture disableremoteplayback'} {'data-hold-last-frame' if hold_last_frame else ''} muted playsinline {'loop' if loop else ''} preload="none" poster="assets/posters/{name}.webp" width="{'540' if portrait else '1280'}" height="{'960' if portrait else '720'}" aria-label="{escape(label)}">
        <source data-src="assets/media/{name}.mp4" type="video/mp4">
      </video>{f'<span class="speed-label">{speed}</span>' if speed else ''}
      <button class="video-start" aria-label="Play {escape(label)}"><span aria-hidden="true">▶</span> {escape(button_label or label)}</button>
      {('<div class="video-controls"><button class="video-toggle" type="button" aria-label="Pause ' + escape(label) + '">Pause</button><button class="video-fullscreen" type="button" aria-label="Full screen: ' + escape(label) + '">⛶</button></div>') if name != 'supplementary' else ''}
      {('<div class="film-caption" aria-hidden="true"><span class="live-dot"></span><span id="hero-scene">Contact, leverage, retrieve</span><span id="hero-index">01 / 03</span></div>') if autoplay else ''}
    </div>'''


def heading(num, subject, title, copy):
    return f'<div class="section-heading"><p class="eyebrow">{num} / {subject}</p><h2>{title}</h2><p>{copy}</p></div>'


def detail(title, content, *, expanded=False):
    return f'<details class="research-details" {"open" if expanded else ""}><summary>{title}<span aria-hidden="true">+</span></summary><div class="details-content">{content}</div></details>'


def figure(name, alt, caption):
    return f'<figure><button class="zoom-figure" data-zoom="assets/figures/{name}.webp" aria-label="Enlarge {escape(alt)}"><img src="assets/figures/{name}.webp" alt="{escape(alt)}" loading="lazy"></button><figcaption>{caption}</figcaption></figure>'


def zoom_asset(name, alt, width, height):
    return f'<button class="zoom-figure" data-zoom="assets/figures/{name}.webp" aria-label="Enlarge {escape(alt)}"><img src="assets/figures/{name}.webp" width="{width}" height="{height}" alt="{escape(alt)}" loading="lazy"></button>'


def challenge_visual(kind, anchor, link):
    if kind == 'skill':
        media = film('challenge-skill', 'contact-aware execution and recovery', loop=False, button_label='Play skill example')
        caption = '<strong>Contact-aware execution, through a hand skill.</strong> Key turning and thin-handle retrieval illustrate precise contact and recovery. The hand skill executes finger contacts; coordination controls arm motion and activation.'
    elif kind == 'intervention':
        media = '<div class="intervention-comparison"><div class="comparison-clips">'
        for name, title, duration in [('intervention-full-dof', 'Full-DoF HIL-SERL', '7 s'), ('intervention-hifun', 'HiFun', '7 s')]:
            media += f'<div class="comparison-clip"><div class="comparison-clip-heading"><h5>{title}</h5><span>{duration}</span></div>' + film(name, title, button_label='Play video') + '</div>'
        media += '</div><button class="play-comparison button" type="button">Play both</button></div>'
        caption = '<strong>Explore arm motion and skill activation.</strong> HiFun delegates finger execution to a learned hand skill. This avoids direct full-DoF arm-hand exploration and enables more efficient real-world learning.'
    elif kind == 'critic':
        media = '<div class="critic-design-evidence"><div class="critic-method"><p class="visual-label">Method overview</p>'
        media += zoom_asset('method-critic', 'Multi-head critic from the method overview: navigation alignment and modulation timing.', 138, 144)
        media += '</div><div class="critic-experiment"><p class="visual-label">Experimental evidence</p><div class="challenge-plots">'
        for name, alt, width in [('critic-error', 'P95 activation error: HiFun 2.00 cm; without multi-head critic 4.58 cm.', 245), ('critic-far-activation', 'Far activation: HiFun 3.7 percent; without multi-head critic 6.0 percent.', 250)]:
            media += zoom_asset(name, alt, width, 410)
        media += '</div></div></div>'
        caption = '<strong>Separate value heads, better activation placement.</strong> Left: the multi-head critic in the original method overview. Right: Appendix Fig. 4A on Angle-Spreader Retrieval. Blue = HiFun; orange = without multi-head critic.'
    else:
        media = '<div class="iaw-method"><p class="visual-label">Method overview</p>'
        media += zoom_asset('method-iaw', 'Intervention advantage weighting from the method overview: compare human and policy action values to control imitation strength.', 233, 144)
        media += '</div>'
        caption = '<strong>Judge a correction by the improvement it offers.</strong><p>A critic trained on real-world outcomes predicts the return of each candidate action. Comparing the intervention with the current policy action in the same state estimates how much the correction improves on the robot’s own behavior. IAW gives higher-advantage corrections more imitation weight and limits the influence of low-advantage corrections, focusing learning on guidance expected to improve execution.</p>'
    evidence_link = f' <a class="evidence-link" href="{anchor}">{link} ↓</a>' if anchor else ''
    return f'<figure class="challenge-media" data-kind="{kind}">{media}<figcaption>{caption}{evidence_link}</figcaption></figure>'


html = '''<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HiFun | Functional Dexterous Manipulation</title>
<meta name="description" content="HiFun learns contact-aware hand skills and when to use them. Hierarchical real-world RL for functional dexterity, evaluated on six tasks with two dexterous hands.">
<meta name="theme-color" content="#f6f4ef"><meta property="og:type" content="website">
<meta property="og:title" content="HiFun: Learning contact skills and when to use them">
<meta property="og:description" content="Contact-aware hand skills. Learned coordination. 295 successful evaluation trials out of 300 across six real-world tasks.">
<link rel="canonical" href="https://hifun-cfu.pages.dev/">
<meta property="og:url" content="https://hifun-cfu.pages.dev/">
<meta property="og:image" content="https://hifun-cfu.pages.dev/assets/posters/hero.webp">
<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/fonts/fonts.css"><link rel="stylesheet" href="styles.css"><script src="script.js" defer></script>
</head><body><a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><nav class="nav container" aria-label="Main navigation"><a class="brand" href="#top" aria-label="HiFun home"><span class="brand-symbol" aria-hidden="true"><i></i><i></i></span>HiFun</a><button class="menu-toggle" aria-expanded="false" aria-controls="nav-links">Menu <span aria-hidden="true">☰</span></button><div class="nav-links" id="nav-links"><a href="#overview">Overview</a><a href="#demos">Task Challenges</a><a href="#method">Method</a><a href="#results">Results</a><a href="#challenges">Insights</a><a href="#citation-section">Citation</a></div></nav><div class="progress-track" aria-hidden="true"><span id="progress"></span></div></header>
<main id="main"><section class="hero" id="top"><div class="container hero-inner"><p class="eyebrow">Real-world robot learning</p><div class="wordmark" aria-hidden="true">Hi<span>Fun</span></div><h1>A Hierarchical Framework for Efficient<br class="desktop-break"> Functional Dexterous Manipulation Learning</h1>
<p class="conference-badge">Accepted to <strong>CoRL 2026</strong></p>
<div class="authors" aria-label="Authors"><a href="https://hly-123.github.io/" target="_blank" rel="noopener noreferrer">Linyi Huang<sup>1</sup></a><span>Guowei Huai<sup>1</sup></span><a href="https://scholar.google.com/citations?user=P0IYZdYAAAAJ&amp;hl=en" target="_blank" rel="noopener noreferrer">Weibin Liu<sup>1</sup></a><a href="https://scholar.google.com/citations?user=stsR9BcAAAAJ&amp;hl=en" target="_blank" rel="noopener noreferrer">Shulong Jiang<sup>1</sup></a><a href="https://scholar.google.com/citations?user=XhyKVFMAAAAJ&amp;hl=en" target="_blank" rel="noopener noreferrer">Ping Tan<sup>2</sup></a><a href="https://scholar.google.com/citations?user=0zZ27MgAAAAJ&amp;hl=en" target="_blank" rel="noopener noreferrer">Weixuan Zhang<sup>1</sup></a><a href="https://zdchan.github.io/" target="_blank" rel="noopener noreferrer">Hui Zhang<sup>3</sup></a><a href="https://scholar.google.com/citations?user=kBN1B6YAAAAJ&amp;hl=en" target="_blank" rel="noopener noreferrer">Jie Song<sup>1,2</sup></a></div>
<p class="affiliations"><span><sup>1</sup> HKUST (Guangzhou)</span><span><sup>2</sup> HKUST</span><span><sup>3</sup> ETH Zurich</span></p>
<div class="resource-buttons"><a class="button button-dark" href="#full-video">Overview video ↗</a><button class="button button-coming-soon" type="button" disabled>Paper · Coming soon</button><a class="button code-repository" href="https://github.com/Hly-123/HiFun-code" aria-label="HiFun official code — coming soon. Star the repository on GitHub.">Code · Coming soon ↗</a></div>
</div></section>
<section class="overview" id="overview"><div class="container"><h2 class="overview-title">Overview</h2><figure class="full-video" id="full-video">
'''
html += film('supplementary', 'overview video', loop=False, button_label='Play video') + '</figure>'
html += '</div></section><section class="section section-white" id="abstract"><div class="container abstract-container"><p class="eyebrow">The full picture</p><h2>Abstract</h2>'
html += '''<div class="abstract"><p>While multi-fingered dexterous robot hands have the potential to provide human-level dexterity, using them for functional manipulation remains difficult because task success depends on precise contact, coordinated arm-hand motion, and reactive recovery from execution errors. Precise contact depends on complex contact dynamics that are difficult to model accurately in simulation, motivating real-world learning. However, real-world demonstrations in the full arm-hand control space are costly and noisy because each trajectory must coordinate arm motion with high-DoF multi-finger contact. Small execution deviations can further cause slipped contact or premature force application, making recovery from off-nominal contact states important for robust execution.</p><p>To deal with these challenges, we propose HiFun, a hierarchical real-world RL framework for functional dexterous manipulation tasks. Our key insight is to decouple the control complexity into a functional hand skill for precise contact execution and an arm-hand coordination policy for arm control and hand-skill activation. This design enables effective real-time human intervention for reactive recovery learning and efficient data collection with Dynamic Movement Primitive (DMP) augmentation. Across six real-world tasks on two dexterous hands, HiFun achieves 98.3% average success within one hour of online training and remains robust to dynamic disturbances.</p></div>'''
html += '</div></section>'

html += '<section class="section section-white" id="demos"><div class="container">'
html += heading('01', 'Task challenges', 'What makes functional dexterity challenging?', 'Functional dexterous tasks demand precise contact, coordinated arm–hand motion, and recovery from small execution errors. Constrained tool retrieval brings these requirements together in a single task.')
html += '<div class="demo-layout"><figure>' + film('position-disturbances', 'Watch the contact sequence') + '<figcaption>Tool retrieval under position disturbances · Sharpa hand</figcaption></figure><ol class="contact-sequence">'
for i, (title, text) in enumerate([
    ('Precise contact', 'Place fingertips on the exposed handle and regulate force as contact changes.'),
    ('Arm–hand coordination', 'Coordinate arm motion and multi-finger levering to create clearance and form a precision grasp.'),
    ('Reactive recovery', 'Small slips or misalignment can interrupt the sequence, requiring contact or alignment to be restored before continuing.'),
], 1):
    html += f'<li><span>0{i}</span><div><h3>{title}</h3><p>{text}</p></div></li>'
html += '</ol></div></div></section>'

html += '<section class="section section-white" id="method"><div class="container">'
html += heading('02', 'Method', 'Learn contact skills.<br>Coordinate their execution.', 'HiFun separates learning how the fingers make contact from learning where and when to use that contact. First, residual RL refines a kinesthetic reference into a contact-aware hand skill. With this skill frozen, a coordination policy learns arm motion and skill activation, starting from DMP rollouts and improving through value-guided human-in-the-loop learning. At execution time, the two policies work together to approach the target and perform fine-grained contact.')
html += '<div class="complete-method-figure">' + figure('method', 'Complete HiFun framework', '') + '</div>'
html += '</div></section><section class="section" id="results"><div class="container">'
html += heading('03', 'Real-world evaluation', 'Functional dexterous tasks.', 'Each task is evaluated over 50 trials with randomized object poses inside the trained workspace. Success requires completing the functional outcome.')
html += '<div class="task-grid">'
tasks = [
    ('A', 'Precise tool use', 'Sharpa', 'Power-Drill Actuation', 'power-drill', 50, 'Tighten the target screw while maintaining alignment and actuating the trigger.'),
    ('B', 'Constrained space', 'Sharpa', 'Angle-Spreader Retrieval', 'angle-spreader-40s', 50, 'Establish fingertip contact and fully extract the tool from its constrained tray.'),
    ('C', 'Constrained space', 'Sharpa', 'Thin-Handle Retrieval', 'thin-handle', 50, 'Lever an exposed handle into reach, form a precision grasp and fully extract it.'),
    ('D', 'Contact-rich rotation', 'Sharpa', 'Power-Drill Bit Removal', 'bit-removal', 50, 'Maintain multi-finger contact while loosening the chuck, then remove the drill bit.'),
    ('E', 'Precise tool use', 'XHand', 'Pipette Dispensing', 'pipette-adaptation', 45, 'Three dispensing executions, side by side. The hand aligns the pipette with each vial and adapts as the vial position changes.'),
    ('F', 'Constrained space', 'XHand', 'Thin-Shaft Tool Retrieval', 'thin-shaft', 50, 'Use a fingertip contact sequence to fully retrieve a thin shaft embedded in foam.')]
for code, category, hand, title, name, count, copy in tasks:
    if code == 'E':
        html += '</div><div class="subsection-heading" id="cross-hand"><p class="eyebrow">Across hand embodiments</p><h3>One framework, different dexterous hands</h3><p>HiFun deploys on both Sharpa and XHand. XHand demonstrations span pipette dispensing, constrained tool retrieval, drill operation, and faucet manipulation.</p></div><div class="task-grid xhand-tasks">'
    html += f'<article class="task"><div class="task-heading"><div><span class="task-category">{code} / {category} · {hand}</span><h3>{title}</h3></div></div>' + film(name, title, speed='1.5×' if name == 'thin-shaft' else '', loop=False, hold_last_frame=name == 'pipette-adaptation') + f'<p>{copy}</p></article>'
for title, name, copy in [
    ('Power-Drill Operation', 'xhand-drill', 'Coordinate tool alignment and trigger actuation while handling changes in the target position.'),
    ('Faucet Operation', 'xhand-faucet', 'Maintain finger contact to operate the faucet handle during physical interaction.')]:
    html += f'<article class="xhand-demo"><div class="task-heading"><div><span class="task-category">Additional task · XHand</span><h3>{title}</h3></div></div>' + film(name, title, loop=False) + f'<p>{copy}</p></article>'
html += '</div>'
html += '<div class="subsection-heading" id="more-dexterous-tasks"><p class="eyebrow">Across tasks and hands</p><h3>More successful deployment</h3></div>'
html += '<div class="more-tasks-feature"><figure>' + film('deployment-montage', 'Nine-view deployment montage', loop=False) + '</figure><figure>' + film('more-dexterous-tasks', 'More dexterous tasks on XHand', loop=False) + '</figure></div>'
html += '<div class="subsection-heading" id="recovery-transfer"><p class="eyebrow">Beyond nominal rollouts</p><h3>Recovery &amp; Generalization</h3><p>HiFun adapts to position disturbances, object-size changes, and disruptions in fingertip contact.</p></div><div class="extension-grid">'
html += '<figure>' + film('position-disturbances', 'Position disturbances') + '<figcaption><strong>Position disturbances.</strong> When the tool’s position is disturbed, HiFun re-establishes alignment and contact to continue the retrieval.</figcaption></figure>'
html += '<figure>' + film('size-transfer', 'Object-size generalization', speed='2×') + '<figcaption><strong>Object-size generalization.</strong> The same learned hand skill transfers from a 7.5 cm tool to smaller 6.5 cm and 5.5 cm variants.</figcaption></figure></div>'

html += '<div class="finger-adaptation" id="contact-evidence"><figure class="wide-evidence">' + film('contact-recovery', 'Watch finger-level adaptation', speed='1×') + '<figcaption><strong>Finger-level adaptation.</strong> After a collision rotates the key and breaks thumb contact, the hand skill adjusts the fingers to restore contact without arm re-alignment.</figcaption></figure>'
html += '<figure class="recovery-sequence"><div class="recovery-scroll" role="region" tabindex="0" aria-label="Five-frame contact recovery sequence; scroll horizontally for detail"><button class="zoom-figure" data-zoom="assets/figures/key-recovery-sequence.png" aria-label="Enlarge the five-frame contact recovery sequence"><img src="assets/figures/key-recovery-sequence.png" width="7421" height="1109" loading="lazy" alt="Five frames: an unexpected hand–object collision reverses the key rotation; abnormal thumb contact triggers reference-state rewind; residual finger adjustment restores thumb contact. Original arrows, equations and timestamps are preserved."></button></div><figcaption><strong>Contact disruption → reference rewind → residual adjustment → restored contact.</strong> <span class="scroll-hint">Swipe or use the arrow keys to inspect all five frames.</span> Click the figure to enlarge.</figcaption></figure>' + '</div>'

html += '<div class="subsection-heading" id="long-horizon"><p class="eyebrow">Long-horizon manipulation</p><h3>Multiple skills, one policy</h3><p>Here, HiFun runs on XHand in a longer functional sequence. The policy turns the key, grasps the drill, and places it into the drawer by coordinating different hand skills. This shows that HiFun can deploy across dexterous hands and integrate multiple skills in one policy.</p></div>'
html += '<figure class="long-horizon-feature">' + film('long-horizon', 'Watch the long-horizon sequence', speed='1.3×', loop=False) + '<figcaption><strong>Turn the key → grasp the drill → place it in the drawer.</strong> Coordinated execution on XHand.</figcaption></figure></div></section>'
html += '<section class="section" id="challenges"><div class="container">'
html += heading('04', 'Learning challenges and design', 'Challenges &amp; Insights', 'Learning these behaviors directly in the full arm–hand action space makes exploration and human correction difficult. HiFun structures the control interface and learning signals to make real-world learning more efficient.')
challenges = [
    ('High-dimensional exploration',
     'Direct arm–hand RL must discover arm motion, coordinated finger contacts, and activation timing in a coupled action space. Successful contact sequences occupy only a small part of that space.',
     'Explore through contact-aware skills.',
     'Learn finger execution separately, then let the coordination policy explore 6D arm motion and hand-skill activation.',
     'skill',
     None, ''),
    ('Difficult finger-level intervention',
     'Real-time correction of many coupled finger joints is difficult to deliver consistently, especially when human and robot hand morphologies differ.',
     'Make the skill the intervention interface.',
     'Operators correct arm placement and skill activation through the learned hand skill, reducing the need to teleoperate individual finger joints.',
     'intervention',
     '#method', 'Explore the skill-level interface'),
    ('Ambiguous credit assignment',
     'The same unsuccessful outcome can result from poor arm alignment or mistimed hand-skill activation. A terminal success signal alone does not distinguish these causes.',
     'Separate alignment and activation value learning.',
     'Use distinct navigation and modulation targets, with action-subspace gradient routing, to guide arm motion and skill timing.',
     'critic',
     None, ''),
    ('Heterogeneous human supervision',
     'Human corrections can be noisy, delayed, or hesitant. Their usefulness also depends on what the current policy would do in the same state.',
     'Imitate according to estimated advantage.',
     'IAW weights each correction relative to the current policy action, giving stronger imitation weight to corrections with higher critic-estimated advantage.',
     'iaw',
     None, '')]
for i, (topic, challenge, insight, response, media_kind, anchor, link) in enumerate(challenges, 1):
    html += f'''<article class="challenge-row" id="challenge-{media_kind}"><div class="challenge-problem"><p class="challenge-label">0{i} / Challenge</p><h3>{topic}</h3><p>{challenge}</p></div><div class="challenge-response"><p class="challenge-label text-coord">HiFun insight</p><h4>{insight}</h4><p>{response}</p></div>{challenge_visual(media_kind, anchor, link)}</article>'''
html += '</div></section>'

html += '<section class="hero highlights section-white" id="highlights"><div class="container hero-inner"><h2 class="hero-thesis">Learning <span class="text-skill">contact skills</span> and <span class="text-coord">when to use them.</span></h2>'
html += film('hero', 'Watch HiFun', autoplay=True)
html += '''<div class="film-footnote"><span>25 seconds · real robot executions · edited excerpts</span><span>Recovery includes an additional key-turning example.</span></div>
<div class="headline-metrics" aria-label="Main evaluation summary"><div><strong>295<span>/300</span></strong><p>successful evaluation trials</p></div><div><strong>6</strong><p>functional manipulation tasks</p></div><div><strong>2</strong><p>dexterous hand embodiments</p></div><div><strong>≤60<span> min</span></strong><p>online HIL per task</p></div></div>
<p class="source-note hero-note">98.3% mean success over 50 trials per task. The ≤60-minute budget covers online HIL; the full pipeline averages approximately 109 min/task.</p></div></section>'''

html += '<section class="section section-white citation-only" id="citation-section"><div class="container">'
html += '''<div class="citation-section"><div class="citation-heading"><h2>Citation</h2><button class="copy-button" id="copy-citation">Copy BibTeX</button></div><pre id="citation"><code>@inproceedings{huang2026hifun,
  title = {HiFun: a Hierarchical Framework for Efficient
           Functional Dexterous Manipulation Learning},
  author = {Huang, Linyi and Huai, Guowei and Liu, Weibin and
            Jiang, Shulong and Tan, Ping and Zhang, Weixuan and
            Zhang, Hui and Song, Jie},
  booktitle = {Conference on Robot Learning (CoRL)},
  year = {2026}
}</code></pre><span id="copy-status" class="sr-only" role="status"></span></div></div></section></main>
<footer><div class="container footer-inner"><a class="brand" href="#top">HiFun</a><p>Contact-aware skills. Learned coordination.</p><a href="#top">Back to top ↑</a></div></footer>
<dialog id="figure-dialog" aria-labelledby="figure-dialog-title"><div class="dialog-toolbar"><h2 id="figure-dialog-title">Research figure</h2><button id="close-figure" aria-label="Close enlarged figure">Close ×</button></div><div class="dialog-image-scroll" tabindex="0" role="region" aria-label="Enlarged research figure"><img id="enlarged-figure" alt=""></div></dialog>
<noscript><style>.video-start{display:none}.menu-toggle{display:none}.nav-links{display:flex!important}</style><p class="noscript-note">JavaScript is disabled. <a href="assets/media/supplementary.mp4">Watch the overview video directly.</a> Research text, figures and documents remain available.</p></noscript>
</body></html>'''

html = html.replace('<h1>A Hierarchical', '<h1><span class="sr-only">HiFun: </span>A Hierarchical')
style_version = hashlib.sha256((ROOT / 'styles.css').read_bytes()).hexdigest()[:12]
html = html.replace('href="styles.css"', f'href="styles.css?v={style_version}"')
script_version = hashlib.sha256((ROOT / 'script.js').read_bytes()).hexdigest()[:12]
html = html.replace('src="script.js"', f'src="script.js?v={script_version}"')
html = '\n'.join(line.rstrip() for line in html.splitlines()) + '\n'
(ROOT / 'index.html').write_text(html, encoding='utf-8')
print('Built index.html')
