'use strict';

// Each source is attached only after a playback request. Only the hero opts into autoplay.
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const videoStates = new Map();
const visibilityObserver = new IntersectionObserver(entries => {
  for (const entry of entries) {
    const video = entry.target;
    const state = videoStates.get(video);
    state.visible = entry.isIntersecting && entry.intersectionRatio >= 0.15;
    if (!state.visible) pauseOffscreen(video, state);
    else if (state.wantsPlayback && !document.hidden) attemptPlay(video, state);
  }
}, {threshold: [0, 0.15, 0.5]});

async function loadVideo(video) {
  const source = video.querySelector('source[data-src]');
  if (source && !source.hasAttribute('src')) {
    // Pages serves full MP4 responses without byte ranges. A local Blob gives
    // native video controls a seekable source, while keeping the site static.
    if (location.hostname.endsWith('.pages.dev')) {
      const response = await fetch(source.dataset.src);
      if (!response.ok) throw new Error('Video download failed');
      const blob = await response.blob();
      video.src = URL.createObjectURL(blob);
    }
    source.src = source.dataset.src;
    video.load();
  }
}

async function attemptPlay(video, state) {
  if (state.pending || !video.paused) return;
  state.pending = true;
  const button = state.frame.querySelector('.video-start');
  const label = button.innerHTML;
  button.textContent = 'Loading video…';
  button.disabled = true;
  try {
    await loadVideo(video);
    if (!state.visible || document.hidden || !state.wantsPlayback) return;
    await video.play();
    if (!state.visible || document.hidden) pauseOffscreen(video, state);
  } catch (error) {
    // Autoplay restrictions leave the poster and explicit play button available.
    if (error.name !== 'AbortError') state.frame.classList.remove('is-started');
  } finally {
    state.pending = false;
    button.disabled = false;
    button.innerHTML = label;
  }
}

function pauseOffscreen(video, state) {
  if (!video.paused) {
    state.environmentPause = true;
    video.pause();
  }
}

document.querySelectorAll('.managed-video').forEach(video => {
  const frame = video.closest('.media-frame');
  const state = {frame, visible:false, wantsPlayback:video.hasAttribute('data-autoplay') && !reduceMotion.matches, pending:false, environmentPause:false};
  videoStates.set(video, state);
  frame.querySelector('.video-start').addEventListener('click', () => {
    state.wantsPlayback = true;
    state.visible = true;
    state.environmentPause = false;
    if (video.ended) video.currentTime = 0;
    attemptPlay(video, state);
  });
  video.addEventListener('playing', () => {
    frame.classList.add('is-started');
    state.wantsPlayback = true;
  });
  video.addEventListener('pause', () => {
    if (state.environmentPause) state.environmentPause = false;
    else state.wantsPlayback = false;
  });
  video.addEventListener('ended', () => {
    state.wantsPlayback = false;
    if (!video.hasAttribute('data-hold-last-frame')) frame.classList.remove('is-started');
  });
  video.addEventListener('error', () => {
    state.wantsPlayback = false;
    const button = frame.querySelector('.video-start');
    frame.classList.remove('is-started');
    button.textContent = 'Video unavailable · retry';
    button.setAttribute('aria-label', 'Retry loading video');
    const source = video.querySelector('source');
    if (source) source.removeAttribute('src');
  });
  visibilityObserver.observe(video);
});

// Comparison clips retain their own clocks; no speed matching is applied.
document.querySelectorAll('.play-comparison').forEach(button => {
  const videos = [...button.closest('.intervention-comparison').querySelectorAll('video')];
  const updateLabel = () => { button.textContent = videos.some(video => !video.paused) ? 'Pause both' : 'Play both'; };
  videos.forEach(video => { video.addEventListener('play', updateLabel); video.addEventListener('pause', updateLabel); });
  button.addEventListener('click', () => {
    const pause = videos.some(video => !video.paused);
    for (const video of videos) {
      const state = videoStates.get(video);
      state.wantsPlayback = !pause;
      state.environmentPause = false;
      if (pause) video.pause();
      else if (state.visible) attemptPlay(video, state);
    }
    updateLabel();
  });
});

document.addEventListener('visibilitychange', () => {
  for (const [video, state] of videoStates) {
    if (document.hidden) pauseOffscreen(video, state);
    else if (state.visible && state.wantsPlayback) attemptPlay(video, state);
  }
});
reduceMotion.addEventListener('change', () => {
  if (!reduceMotion.matches) return;
  for (const [video, state] of videoStates) {
    if (video.hasAttribute('data-autoplay')) {
      state.wantsPlayback = false;
      pauseOffscreen(video, state);
    }
  }
});

const heroVideo = document.querySelector('#hero-video');
heroVideo.addEventListener('timeupdate', () => {
  const scene = heroVideo.currentTime < 7 ? 0 : heroVideo.currentTime < 18 ? 1 : 2;
  document.querySelector('#hero-scene').textContent = ['Contact, leverage, retrieve', 'Align the tool, actuate the trigger', 'Lose contact, adapt, recover'][scene];
  document.querySelector('#hero-index').textContent = `0${scene + 1} / 03`;
});

const menuButton = document.querySelector('.menu-toggle');
const nav = document.querySelector('#nav-links');
function closeMenu() {
  menuButton.setAttribute('aria-expanded', 'false');
  nav.classList.remove('is-open');
}
menuButton.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  nav.classList.toggle('is-open', open);
});
nav.addEventListener('click', event => {if (event.target.closest('a')) closeMenu();});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menuButton.focus();
  }
});

const links = [...nav.querySelectorAll('a')];
const sections = links.map(link => document.querySelector(link.hash));
let scrollPending = false;
function updateScroll() {
  const available = document.documentElement.scrollHeight - innerHeight;
  document.querySelector('#progress').style.width = `${available > 0 ? Math.min(100, scrollY / available * 100) : 0}%`;
  let active = -1;
  sections.forEach((section, index) => {if (section.getBoundingClientRect().top < innerHeight * .35) active = index;});
  links.forEach((link, index) => {
    link.classList.toggle('active', index === active);
    if (index === active) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  scrollPending = false;
}
function scheduleScroll() {if (!scrollPending) {scrollPending = true; requestAnimationFrame(updateScroll);}}
addEventListener('scroll', scheduleScroll, {passive:true});
addEventListener('resize', scheduleScroll);
document.querySelectorAll('details').forEach(details => details.addEventListener('toggle', scheduleScroll));
updateScroll();

const dialog = document.querySelector('#figure-dialog');
let figureTrigger = null;
document.querySelectorAll('[data-zoom]').forEach(button => button.addEventListener('click', () => {
  figureTrigger = button;
  const image = document.querySelector('#enlarged-figure');
  image.src = button.dataset.zoom;
  image.alt = button.querySelector('img').alt;
  document.querySelector('#figure-dialog-title').textContent = button.getAttribute('aria-label').replace(/^Enlarge /, '');
  dialog.classList.toggle('is-panorama', button.closest('.recovery-sequence') !== null);
  dialog.querySelector('.dialog-image-scroll').scrollLeft = 0;
  dialog.showModal();
}));
document.querySelector('#close-figure').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => {if (event.target === dialog) dialog.close();});
dialog.addEventListener('close', () => {if (figureTrigger) figureTrigger.focus();});

document.querySelector('#copy-citation').addEventListener('click', async () => {
  const button = document.querySelector('#copy-citation');
  const citation = document.querySelector('#citation');
  const status = document.querySelector('#copy-status');
  try {
    await navigator.clipboard.writeText(citation.textContent);
    button.textContent = 'Copied';
    status.textContent = 'BibTeX copied to clipboard.';
    setTimeout(() => {button.textContent = 'Copy BibTeX';}, 2000);
  } catch {
    const range = document.createRange();
    range.selectNodeContents(citation);
    const selection = getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    button.textContent = 'Selected · press Ctrl/Cmd+C';
    status.textContent = 'Citation selected. Press Control C or Command C to copy.';
  }
});
