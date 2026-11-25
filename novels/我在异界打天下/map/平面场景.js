import { bindPicking } from './立体场景.js';
import { regionAt, width, depth } from './地形.js';

// The fallback uses exactly the same cartography, region boundaries and labels.
export function createFlatScene(host, surface, events) {
  const canvas = document.createElement('canvas'), ctx = canvas.getContext('2d');
  canvas.setAttribute('aria-label', '武元大陆交互平面图，可点击任一区域');
  host.append(canvas);
  let scale = 1, dx = 0, dy = 0, box = [0, 0, 1, 1], drag = null, frame = 0;
  function draw() {
    frame = 0;
    const w = host.clientWidth, h = host.clientHeight, dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (!w || !h) return;
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, w, h);
    const imageW = Math.min(w * .94, h * 1.5 * .94) * scale, imageH = imageW / 1.5;
    dx = Math.max(-imageW / 2, Math.min(imageW / 2, dx)); dy = Math.max(-imageH / 2, Math.min(imageH / 2, dy));
    box = [(w - imageW) / 2 + dx, (h - imageH) / 2 + dy, imageW, imageH];
    ctx.drawImage(surface, ...box);
    events.project(p => [box[0] + (p.x / width + .5) * imageW, box[1] + (p.z / depth + .5) * imageH], 0, scale);
  }
  function invalidate() { if (!frame) frame = requestAnimationFrame(draw); }
  function zoom(factor) { scale = Math.max(.7, Math.min(5, scale * factor)); invalidate(); }
  function reset() { scale = 1; dx = dy = 0; invalidate(); }
  function locate(e) {
    const r = canvas.getBoundingClientRect();
    return regionAt((e.clientX - r.left - box[0]) / box[2], (e.clientY - r.top - box[1]) / box[3]);
  }
  function down(e) {
    if (e.button !== 0 || !e.isPrimary) { drag = null; return; }
    drag = [e.clientX - dx, e.clientY - dy]; canvas.setPointerCapture(e.pointerId);
  }
  function move(e) {
    if (!drag || !e.isPrimary) return;
    dx = e.clientX - drag[0]; dy = e.clientY - drag[1]; invalidate();
  }
  function end() { drag = null; }
  function wheel(e) { e.preventDefault(); zoom(Math.exp(-e.deltaY * .0015)); }
  const handlers = { pointerdown: down, pointermove: move, pointerup: end, pointercancel: end, wheel };
  const removePicking = bindPicking(canvas, locate, events);
  for (const [name, fn] of Object.entries(handlers)) canvas.addEventListener(name, fn, { passive: false });
  const observer = new ResizeObserver(invalidate); observer.observe(host); invalidate();
  return {
    reset, setView: reset, zoom, invalidate, updateTexture: invalidate,
    dispose() {
      for (const [name, fn] of Object.entries(handlers)) canvas.removeEventListener(name, fn);
      removePicking(); observer.disconnect(); cancelAnimationFrame(frame); canvas.remove();
    }
  };
}
