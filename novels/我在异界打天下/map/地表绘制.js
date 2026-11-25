import { regions, placeById, routes } from './地理资料.js';
import { getField, regionAt, sampleHeight, smooth, mix, rivers, curvePoints } from './地形.js';

const w = 1200, h = 800, maskWidth = 480, maskHeight = 320;

function canvas(width = w, height = h) {
  const node = document.createElement('canvas');
  node.width = width;
  node.height = height;
  return node;
}

export function seededRandom(seed) {
  return () => {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    return seed / 4294967296;
  };
}

function trace(ctx, line) {
  ctx.beginPath();
  line.forEach(([u, v], i) => i ? ctx.lineTo(u * w, v * h) : ctx.moveTo(u * w, v * h));
}

const lowColors = {
  shuo: [164, 177, 135], steppe: [187, 186, 136], west: [177, 162, 125],
  central: [206, 190, 142], east: [136, 161, 124], ports: [186, 183, 140],
  sea: [153, 170, 135], isles: [158, 176, 135]
};

function paintRelief(ctx) {
  const field = getField(), pixels = ctx.createImageData(w, h), data = pixels.data;
  const random = seededRandom(833), regionGrid = new Uint8Array(maskWidth * maskHeight);
  const ids = Object.fromEntries(regions.map((r, i) => [r.id, i]));
  for (let y = 0; y < maskHeight; y++) {
    for (let x = 0; x < maskWidth; x++) {
      regionGrid[y * maskWidth + x] = ids[regionAt((x + .5) / maskWidth, (y + .5) / maskHeight)];
    }
  }
  for (let y = 0; y < h; y++) {
    const v = (y + .5) / h;
    for (let x = 0; x < w; x++) {
      const u = (x + .5) / w, z = sampleHeight(u, v, field);
      const grain = (random() - .5) * 6;
      let r, g, b;
      if (z <= 0) {
        const deep = smooth(-.16, 5.6, -z);
        const wave = Math.sin(32 * z) * .65 + Math.sin(x * .18 + Math.sin(y * .28)) * .60;
        const shoal = Math.max(0, 1 - Math.abs(z + .29) / .085) * 36
          + Math.max(0, 1 - Math.abs(z + .59) / .075) * 13;
        r = mix(125, 53, deep) + wave + shoal; g = mix(174, 119, deep) + shoal;
        b = mix(158, 121, deep) + wave + shoal;
      } else {
        const region = regions[regionGrid[Math.floor(v * maskHeight) * maskWidth + Math.floor(u * maskWidth)]].id;
        const low = lowColors[region];
        const dx = (sampleHeight(u + .0018, v, field) - sampleHeight(u - .0018, v, field)) / .432;
        const dz = (sampleHeight(u, v + .0027, field) - sampleHeight(u, v - .0027, field)) / .432;
        const length = Math.sqrt(1 + dx * dx + dz * dz);
        const light = (.62 * dx + .36 * dz + .70) / length;
        const shade = (light - .64) * 47;
        const slope = Math.hypot(dx, dz);
        const timber = smooth(1.8, 5.8, z) * .76;
        const mid = smooth(4.5, 11.8, z + Math.min(1.5, slope * .45));
        const high = smooth(9.0, 15.5, z);
        const contourDistance = Math.abs(z / .86 - Math.round(z / .86));
        const contour = (1 - smooth(.005, Math.min(.22, .014 + slope * .12), contourDistance)) * smooth(.22, 1.2, slope) * 20;
        const shadow = shade - contour;
        r = mix(mix(mix(low[0], 104, timber), 174, mid), 230, high) + shadow;
        g = mix(mix(mix(low[1], 137, timber), 169, mid), 222, high) + shadow;
        b = mix(mix(mix(low[2], 105, timber), 139, mid), 191, high) + shadow;
        const sand = 1 - smooth(.02, .40, z);
        r = mix(r, 220, sand); g = mix(g, 208, sand); b = mix(b, 163, sand);
      }
      const p = (y * w + x) * 4;
      data[p] = r + grain; data[p + 1] = g + grain; data[p + 2] = b + grain; data[p + 3] = 255;
    }
  }
  ctx.putImageData(pixels, 0, 0);
  return regionGrid;
}

function paintLandUse(ctx) {
  const random = seededRandom(272);
  for (let i = 0; i < 3800; i++) {
    const u = random(), v = random(), z = sampleHeight(u, v), region = regionAt(u, v);
    const x = u * w, y = v * h;
    if (z < -1 && random() > .66) {
      ctx.strokeStyle = 'rgba(215,232,208,.28)';
      ctx.lineWidth = .8;
      ctx.beginPath(); ctx.moveTo(x, y); ctx.quadraticCurveTo(x + 3, y - 1.3, x + 7 + random() * 5, y);
      ctx.stroke();
    } else if (region === 'central' && z > .6 && z < 2.15 && random() > .38) {
      ctx.save(); ctx.translate(x, y); ctx.rotate(-.18 + .15 * Math.sin(u * 28 + v * 16));
      const side = 3 + random() * 7;
      ctx.fillStyle = random() > .5 ? 'rgba(154,133,77,.19)' : 'rgba(236,219,156,.36)';
      ctx.fillRect(0, 0, side, side * .6);
      ctx.strokeStyle = 'rgba(108,111,72,.24)'; ctx.lineWidth = .7;
      ctx.strokeRect(0, 0, side, side * .6); ctx.restore();
    } else if (z > 4 && z < 13) {
      ctx.strokeStyle = 'rgba(59,74,61,.18)'; ctx.lineWidth = .65;
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 1.2, y + 2); ctx.lineTo(x - 1.8, y + 2.5); ctx.stroke();
    }
  }
}

function paintWaterways(ctx) {
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  for (const river of rivers) {
    const line = river.line;
    for (const [multiplier, ink] of [[1.48, '#c7ccb0'], [1, '#548b83'], [.55, '#78a99c']]) {
      ctx.strokeStyle = ink;
      for (let i = 1; i < line.length; i++) {
        const t = (i - .5) / (line.length - 1);
        ctx.lineWidth = mix(...river.size, t) * w * multiplier;
        trace(ctx, [line[i - 1], line[i]]); ctx.stroke();
      }
    }
  }
}

function prepareRoutes() {
  const layer = canvas(), ctx = layer.getContext('2d');
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  function road(points, ink, pattern) {
    trace(ctx, curvePoints(points));
    ctx.setLineDash([]); ctx.lineWidth = 3.6; ctx.strokeStyle = 'rgba(247,233,184,.65)'; ctx.stroke();
    ctx.setLineDash(pattern); ctx.lineWidth = 1.7; ctx.strokeStyle = ink; ctx.stroke();
  }
  road([[.154,.235],[.166,.276],[.215,.315],placeById.quarry.at,[.251,.425],[.258,.47],[.275,.507]], '#965c38', [5, 4]);
  for (const r of routes) {
    const points = [placeById[r.from].at, ...r.path, placeById[r.to].at];
    road(points, r.kind === 'sea' || r.kind === 'river' ? '#315f64' : '#995332', r.kind === 'planned' ? [1, 5] : [4, 4]);
  }
  return layer;
}

function prepareAreas(grid) {
  const masks = regions.map(() => canvas(maskWidth, maskHeight));
  const edges = regions.map(() => new Path2D());
  const buffers = masks.map(node => node.getContext('2d').createImageData(maskWidth, maskHeight));
  function segment(id, x, y, dx, dy) {
    edges[id].moveTo(x * w / maskWidth, y * h / maskHeight);
    edges[id].lineTo((x + dx) * w / maskWidth, (y + dy) * h / maskHeight);
  }
  for (let y = 0; y < maskHeight; y++) {
    for (let x = 0; x < maskWidth; x++) {
      const i = y * maskWidth + x, id = grid[i], pixels = buffers[id].data;
      pixels.set([246, 190, 111, 255], i * 4);
      if (!x || grid[i - 1] !== id) segment(id, x, y, 0, 1);
      if (!y || grid[i - maskWidth] !== id) segment(id, x, y, 1, 0);
      if (x === maskWidth - 1 || grid[i + 1] !== id) segment(id, x + 1, y, 0, 1);
      if (y === maskHeight - 1 || grid[i + maskWidth] !== id) segment(id, x, y + 1, 1, 0);
    }
  }
  return Object.fromEntries(regions.map((region, i) => {
    masks[i].getContext('2d').putImageData(buffers[i], 0, 0);
    return [region.id, { mask: masks[i], edge: edges[i] }];
  }));
}

let savedAtlas;
export function getAtlas() {
  if (savedAtlas) return savedAtlas;
  const base = canvas(), ctx = base.getContext('2d');
  const grid = paintRelief(ctx);
  paintLandUse(ctx); paintWaterways(ctx);
  savedAtlas = { base, areas: prepareAreas(grid), paths: prepareRoutes() };
  return savedAtlas;
}

export function paintMap(target, { regionId, hovered, showRoutes }) {
  const atlas = getAtlas(), ctx = target.getContext('2d');
  if (target.width !== w || target.height !== h) { target.width = w; target.height = h; }
  ctx.drawImage(atlas.base, 0, 0);
  function highlight(id, active) {
    const area = atlas.areas[id];
    if (!area) return;
    ctx.globalAlpha = active ? .19 : .13;
    ctx.drawImage(area.mask, 0, 0, w, h);
    ctx.globalAlpha = 1;
    ctx.strokeStyle = active ? 'rgba(254,232,184,.72)' : 'rgba(255,244,208,.78)';
    ctx.lineWidth = active ? 3.2 : 2.4; ctx.stroke(area.edge);
    ctx.strokeStyle = active ? '#945f3f' : '#697552';
    ctx.lineWidth = active ? 1.4 : 1; ctx.stroke(area.edge);
  }
  highlight(regionId, true);
  if (hovered !== regionId) highlight(hovered, false);
  if (showRoutes) ctx.drawImage(atlas.paths, 0, 0);
}
