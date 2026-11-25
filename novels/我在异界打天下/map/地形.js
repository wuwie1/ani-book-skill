import { CatmullRomCurve3, Vector3 } from 'three';
import { ImprovedNoise } from 'three/addons/math/ImprovedNoise.js';

export const width = 120;
export const depth = 80;
export const columns = 300;
export const rows = 200;
const noise = new ImprovedNoise();
const clamp = (value, low = 0, high = 1) => Math.max(low, Math.min(high, value));
export const mix = (a, b, t) => a + (b - a) * t;
const bell = n => Math.exp(-n * n);

export function smooth(low, high, value) {
  const t = clamp((value - low) / (high - low));
  return t * t * (3 - 2 * t);
}

const coast = [[0, 1.24], [.36, 1.09], [.43, 1], [.52, .944], [.55, .89], [.605, .866],
  [.625, .823], [.655, .804], [.688, .791], [.707, .756], [.739, .731], [.753, .693],
  [.786, .675], [.808, .677], [.825, .639], [.85, .626], [.878, .647], [.91, .607],
  [.947, .619], [.974, .584], [1, .555]];

export function coastAt(u) {
  let i = 1;
  while (i < coast.length - 1 && coast[i][0] < u) i++;
  const [x, y] = coast[i - 1];
  const [nextX, nextY] = coast[i];
  return mix(y, nextY, (u - x) / (nextX - x))
    + .005 * Math.sin(u * 178) + .003 * Math.sin(u * 457);
}

const islands = [
  [.821, .846, .021, .017, 3.5], [.914, .903, .028, .022, 4.6],
  [.939, .885, .021, .021, 5.3], [.976, .805, .019, .027, 4.6],
  [.957, .823, .018, .015, 3.2], [.894, .941, .015, .012, 2.3],
  [.874, .892, .010, .009, 1.7], [.966, .768, .012, .011, 1.6]
];

// Staggered, adjoining reading areas cover even unlabelled terrain and open water.
export function regionAt(u, v) {
  if (!Number.isFinite(u) || !Number.isFinite(v) || u < 0 || u > 1 || v < 0 || v > 1) return null;
  const portX = (u - .737) / .096;
  const portY = (v - .68) / .104;
  if (portX * portX + portY * portY < 1 + .05 * Math.sin(u * 92)) return 'ports';
  if (v > coastAt(u)) {
    if (u > .785 && v > .804 - (u - .82) * .44 + .014 * Math.sin(u * 42)) return 'isles';
    return 'sea';
  }
  if (u < .221 + .042 * Math.sin(v * 7.6) + .012 * Math.sin(v * 27)) return 'west';
  if (v < .175 + .036 * Math.sin(u * 7 - 1.7) && u < .718 + .019 * Math.cos(v * 16)) return 'steppe';
  if (u > .684 + .023 * Math.sin(v * 15) - .020 * Math.cos(v * 5)) return 'east';
  if (v > .538 + .037 * Math.sin(u * 14 - 2)) return 'central';
  return 'shuo';
}

export function curvePoints(points, steps = points.length * 6) {
  const curve = new CatmullRomCurve3(points.map(([u, v]) => new Vector3(u * width, 0, v * depth)));
  return curve.getPoints(steps).map(p => [p.x / width, p.z / depth]);
}

const riverSources = [
  { size: [0.0029, .008], points: [[0,.132],[.102,.177],[.146,.218],[.191,.266],[.26,.283],[.307,.293],[.341,.315],[.394,.316],[.453,.342],[.488,.354],[.528,.372],[.55,.4],[.547,.433],[.57,.466],[.585,.493],[.581,.538],[.61,.568],[.665,.591],[.686,.626],[.685,.658],[.715,.698],[.759,.725],[.79,.747]] },
  { size: [.0015, .0036], points: [[.774,.118],[.754,.183],[.73,.23],[.726,.281],[.702,.313],[.693,.351],[.66,.378],[.635,.383],[.614,.41],[.608,.444],[.592,.465],[.585,.493]] },
  { size: [.0008, .0023], points: [[.883,.367],[.832,.395],[.799,.438],[.767,.455],[.74,.495],[.70,.536],[.678,.571],[.665,.591]] },
  { size: [.0013, .0037], points: [[.685,.658],[.668,.693],[.641,.721],[.628,.776],[.607,.815],[.611,.858],[.598,.878]] }
];

export const rivers = riverSources.map(r => ({ ...r, line: curvePoints(r.points) }));
const bins = Array.from({ length: 40 }, () => []);
for (const [index, river] of rivers.entries()) {
  for (let i = 1; i < river.line.length; i++) {
    const a = river.line[i - 1], b = river.line[i];
    const dx = (b[0] - a[0]) * width, dz = (b[1] - a[1]) * depth;
    const edge = { x: a[0] * width, z: a[1] * depth, dx, dz, length2: dx * dx + dz * dz,
      level: index === 1 ? mix(3.4, .87, i / river.line.length) : Math.max(.05, 1.72 - b[1] * 1.74) };
    const first = clamp(Math.floor((Math.min(a[1], b[1]) - .09) * bins.length), 0, bins.length - 1);
    const last = clamp(Math.floor((Math.max(a[1], b[1]) + .09) * bins.length), 0, bins.length - 1);
    for (let j = first; j <= last; j++) bins[j].push(edge);
  }
}

function landHeight(u, v, shore) {
  const n = (x, y, z) => noise.noise(x, y, z);
  const warp = n(u * 4, v * 4, 3);
  const west = bell((u - .085 - .049 * Math.sin(v * 11) - .026 * Math.sin(v * 31)) / .108)
    + .47 * bell((u - .19 - .035 * Math.sin(v * 17)) / .066);
  const east = bell((u - (.91 - v * .27) - .038 * Math.cos(v * 16)) / .117);
  const fringe = .41 * bell((v - .012 - .026 * Math.cos(u * 18)) / .09);
  const shoulder = west + east + fringe + .63 * bell((u - .22 - .06 * Math.sin(v * 19)) / .16) * smooth(.73, .99, v);
  const x = u * 8.7 + warp * .76, y = v * 6.1 + warp * .66;
  const ridge = 1 - Math.abs(n(x, y, 11.73) * 1.72);
  const folds = 1 - Math.abs(n(x * 2.5, y * 2.5, 8.32) * 1.6);
  const detail = n(x * 5.5, y * 5.5, 7.43);
  const hills = shoulder * (2.4 + Math.max(0, ridge) ** 2.65 * 7.9 + folds * 2.2 + detail * 1.45);
  const meadow = 1.15 + n(u * 5, v * 4, 9.5) * .85 + n(u * 17, v * 13, 1.31) * .29;
  let h = (meadow + hills) * (.15 + .85 * smooth(0, .071, shore));
  let nearest = 52, base = .6;
  for (const e of bins[clamp(Math.floor(v * bins.length), 0, bins.length - 1)]) {
    const dx = u * width - e.x, dz = v * depth - e.z;
    const t = clamp((dx * e.dx + dz * e.dz) / e.length2);
    const d = (dx - t * e.dx) ** 2 + (dz - t * e.dz) ** 2;
    if (d < nearest) { nearest = d; base = e.level; }
  }
  if (nearest < 49) h = mix(Math.min(h, base), h, smooth(.25, 6.3, Math.sqrt(nearest)));
  return h;
}

let savedField;
export function getField() {
  if (savedField) return savedField;
  const elevations = new Float32Array((columns + 1) * (rows + 1));
  for (let i = 0; i <= columns; i++) {
    const u = i / columns, coastY = coastAt(u);
    for (let j = 0; j <= rows; j++) {
      const v = j / rows, shore = coastY - v;
      let h;
      if (shore >= 0) h = landHeight(u, v, shore);
      else {
        h = -Math.min(5.4, .16 + -shore * 18) + .09 * noise.noise(u * 18, v * 16, 6.1);
        for (const [cx, cy, rx, ry, top] of islands) {
          const d = ((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2;
          if (d < 6) h = Math.max(h, top * (1 - Math.sqrt(d)) + .17 * Math.sin(u * 390 + v * 120));
        }
      }
      elevations[j * (columns + 1) + i] = h;
    }
  }
  savedField = elevations;
  return savedField;
}

export function sampleHeight(u, v, field = getField()) {
  const x = clamp(u) * columns, z = clamp(v) * rows;
  const i = Math.min(Math.floor(x), columns - 1), j = Math.min(Math.floor(z), rows - 1);
  const p = j * (columns + 1) + i, step = columns + 1;
  return mix(mix(field[p], field[p + 1], x - i), mix(field[p + step], field[p + step + 1], x - i), z - j);
}

export function worldAt([u, v], offset = 0) {
  return new Vector3((u - .5) * width, Math.max(0, sampleHeight(u, v)) + offset, (v - .5) * depth);
}
