import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { ImprovedNoise } from 'three/addons/math/ImprovedNoise.js';
import { places } from './地理资料.js';
import { width, depth, rows, columns, worldAt, getField, sampleHeight, regionAt } from './地形.js';
import { seededRandom } from './地表绘制.js';

export function makeTerrainGeometry() {
  const geo = new THREE.PlaneGeometry(width, depth, columns, rows);
  geo.rotateX(-Math.PI / 2);
  const height = getField(), positions = geo.attributes.position;
  for (let i = 0; i < positions.count; i++) positions.setY(i, Math.max(0, height[i]));
  geo.computeBoundingSphere();
  return geo;
}

export function pickTerrainRegion(cast, surfaces, camera, pointer) {
  cast.setFromCamera(pointer, camera);
  const hit = cast.intersectObjects(surfaces, false)[0];
  if (!hit) return null;
  const u = THREE.MathUtils.clamp(hit.point.x / width + .5, 0, 1);
  const v = THREE.MathUtils.clamp(hit.point.z / depth + .5, 0, 1);
  return regionAt(u, v);
}

function homeFraming(geometry, offset) {
  const towardsCamera = offset.clone().normalize();
  const right = new THREE.Vector3(0, 1, 0).cross(towardsCamera).normalize();
  const up = new THREE.Vector3().crossVectors(towardsCamera, right);
  const point = new THREE.Vector3();
  let left = Infinity, bottom = Infinity, top = -Infinity, edge = -Infinity;
  function include(p) {
    const x = p.dot(right), y = p.dot(up);
    left = Math.min(left, x); edge = Math.max(edge, x);
    bottom = Math.min(bottom, y); top = Math.max(top, y);
  }
  const vertices = geometry.attributes.position;
  for (let i = 0; i < vertices.count; i++) include(point.fromBufferAttribute(vertices, i));
  for (const x of [-width / 2, width / 2]) for (const z of [-depth / 2, depth / 2]) include(point.set(x, -3.65, z));
  return { offset, center: right.multiplyScalar((left + edge) / 2).addScaledVector(up, (bottom + top) / 2),
    width: (edge - left) / .94, height: (top - bottom) / .90 };
}

function cutEdges() {
  const vertices = [], colors = [], indices = [];
  const bands = ['#96916c', '#898364', '#afa07a', '#736e58', '#817b64', '#b3a17a', '#6b6959'];
  function side(start, end, steps, shade) {
    let previous = 0;
    for (let i = 0; i <= steps; i++) {
      const t = i / steps, u = start[0] + t * (end[0] - start[0]), v = start[1] + t * (end[1] - start[1]);
      const p = worldAt([u, v]);
      const grain = Math.sin(61 * u + 48 * v) * .13 + Math.cos(121 * u - 32 * v) * .06;
      const heights = [p.y, p.y * .5 - .43 + grain, -.68 + grain, -1.39 + grain, -1.63 + grain, -2.6 + grain, -2.85 + grain, -3.65];
      const first = vertices.length / 3;
      for (let band = 0; band < bands.length; band++) {
        const color = new THREE.Color(bands[band]).multiplyScalar(shade + .045 * Math.sin(i * .38));
        vertices.push(p.x, heights[band], p.z, p.x, heights[band + 1], p.z);
        colors.push(color.r, color.g, color.b, color.r * .93, color.g * .93, color.b * .93);
        if (i) {
          const a = previous + band * 2, b = first + band * 2;
          indices.push(a, b, a + 1, b, b + 1, a + 1);
        }
      }
      previous = first;
    }
  }
  side([0,0], [1,0], columns, .90); side([1,0], [1,1], rows, .78);
  side([1,1], [0,1], columns, 1); side([0,1], [0,0], rows, 1.06);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geo.setIndex(indices);
  return new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide }));
}

function forests() {
  const random = seededRandom(742), noise = new ImprovedNoise(), trees = [];
  for (let i = 0; i < 5900; i++) {
    const u = random(), v = random(), area = regionAt(u, v), y = sampleHeight(u, v);
    const density = noise.noise(u * 21, v * 16, 3.9) + .36 * noise.noise(u * 51, v * 41, 2.4);
    if (y < 1.7 || y > 9.6 || density < (area === 'east' ? -.18 : .25)) continue;
    const scale = (.48 + random() * .61) * (area === 'east' ? 1.12 : .86);
    trees.push({ at: worldAt([u,v]), scale, tone: random(), angle: random() * 6.28 });
  }
  const geo = new THREE.ConeGeometry(.36, 1.38, 6);
  const inst = new THREE.InstancedMesh(geo, new THREE.MeshLambertMaterial({ flatShading: true }), trees.length);
  const object = new THREE.Object3D(), dark = new THREE.Color('#41694f'), light = new THREE.Color('#81926b');
  trees.forEach((tree, i) => {
    object.position.copy(tree.at); object.position.y += tree.scale * .59;
    object.scale.setScalar(tree.scale); object.rotation.y = tree.angle; object.updateMatrix();
    inst.setMatrixAt(i, object.matrix); inst.setColorAt(i, dark.clone().lerp(light, tree.tone));
  });
  return inst;
}

function settlements() {
  const group = new THREE.Group(), box = new THREE.BoxGeometry(1, 1, 1);
  const roof = new THREE.ConeGeometry(1, 1, 4);
  const stone = new THREE.MeshLambertMaterial({ color: '#c7aa7a' });
  const plaster = new THREE.MeshLambertMaterial({ color: '#e4c99b' });
  const tile = new THREE.MeshLambertMaterial({ color: '#925e40' });
  function piece(parent, geo, mat, x, y, z, sx, sy, sz, rotation = 0) {
    const obj = new THREE.Mesh(geo, mat); obj.position.set(x, y, z);
    obj.scale.set(sx, sy, sz); obj.rotation.y = rotation; parent.add(obj);
  }
  for (const place of places.filter(p => p.city)) {
    const city = new THREE.Group(); city.position.copy(worldAt(place.at, .12));
    city.scale.setScalar(place.city); city.rotation.y = -.18;
    piece(city, box, stone, 0, .14, 0, 2.9, .5, 2.2);
    for (const x of [-1.28, 1.28]) piece(city, box, stone, x, .41, 0, .13, .58, 2.0);
    for (const z of [-.94, .94]) piece(city, box, stone, 0, .41, z, 2.64, .58, .13);
    for (const [x,z,s] of [[0,-.16,1],[-.84,.4,.54],[.84,.4,.54],[-.94,-.68,.48],[.94,-.68,.48]]) {
      piece(city, box, plaster, x, .48 + s * .29, z, s * .78, s * .7, s * .66);
      piece(city, roof, tile, x, .5 + s, z, s * .81, s * .56, s * .66, Math.PI / 4);
    }
    group.add(city);
  }
  return group;
}

function sailingBoats() {
  const fleet = new THREE.Group(), sail = new THREE.BufferGeometry();
  sail.setAttribute('position', new THREE.Float32BufferAttribute([0,.24,0, 0,1.55,0, -.72,.30,.1], 3));
  const cloth = new THREE.MeshBasicMaterial({ color: '#ede2bd', side: THREE.DoubleSide });
  const hull = new THREE.ConeGeometry(.4, 1.6, 5);
  const timber = new THREE.MeshLambertMaterial({ color: '#795b40' });
  for (const [u,v,angle] of [[.787,.778,-.4],[.902,.715,.5],[.73,.873,-.6],[.86,.97,.4]]) {
    const boat = new THREE.Group(), body = new THREE.Mesh(hull, timber);
    body.rotation.z = -Math.PI / 2; body.scale.set(.57, 1, .7); boat.add(body, new THREE.Mesh(sail, cloth));
    boat.position.copy(worldAt([u,v], .12)); boat.rotation.y = angle; fleet.add(boat);
  }
  return fleet;
}

function contactShadow() {
  const tex = document.createElement('canvas'); tex.width = 256; tex.height = 168;
  const ctx = tex.getContext('2d');
  ctx.shadowBlur = 10; ctx.shadowColor = '#091512'; ctx.fillStyle = '#14221e';
  ctx.fillRect(18, 15, 220, 137);
  const map = new THREE.CanvasTexture(tex);
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(width * 1.18, depth * 1.24),
    new THREE.MeshBasicMaterial({ map, transparent: true, opacity: .66, depthWrite: false }));
  mesh.rotation.x = -Math.PI / 2; mesh.position.set(0, -3.95, .7);
  return mesh;
}

// A drag, a right click and a two-finger gesture must never select a region.
export function bindPicking(canvas, locate, events) {
  let press = null;
  const active = new Set();
  function down(e) {
    active.add(e.pointerId);
    if (active.size === 1 && e.button === 0) press = { id: e.pointerId, x: e.clientX, y: e.clientY };
    else press = null;
    events.hover(null);
  }
  function move(e) {
    if (press && Math.hypot(e.clientX - press.x, e.clientY - press.y) > 5) press = null;
    if (e.pointerType !== 'touch' && !e.buttons) events.hover(locate(e));
  }
  function up(e) {
    active.delete(e.pointerId);
    if (press?.id === e.pointerId && Math.hypot(e.clientX - press.x, e.clientY - press.y) <= 5) {
      const region = locate(e);
      if (region) events.pick(region);
    }
    press = null;
  }
  function cancel(e) { active.delete(e.pointerId); press = null; }
  function leave() { events.hover(null); }
  const handlers = { pointerdown: down, pointermove: move, pointerup: up, pointercancel: cancel, lostpointercapture: cancel, pointerleave: leave };
  for (const [name, handler] of Object.entries(handlers)) canvas.addEventListener(name, handler);
  return () => { for (const [name, handler] of Object.entries(handlers)) canvas.removeEventListener(name, handler); };
}

export function createScene(host, surface, events) {
  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0, 0); renderer.outputColorSpace = THREE.SRGBColorSpace;
  const canvas = renderer.domElement;
  canvas.setAttribute('aria-label', '武元大陆交互地形，可点击任一区域');
  host.append(canvas);
  const scene = new THREE.Scene(), texture = new THREE.CanvasTexture(surface);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  const terrain = new THREE.Mesh(makeTerrainGeometry(), new THREE.MeshBasicMaterial({ map: texture }));
  const surfaces = [terrain, cutEdges()];
  scene.add(...surfaces, contactShadow(), forests(), settlements(), sailingBoats());
  const sun = new THREE.DirectionalLight('#fff0d0', 1.75); sun.position.set(-35, 65, -25);
  scene.add(sun, new THREE.HemisphereLight('#f5edcf', '#7d8e72', 1.7));
  const camera = new THREE.OrthographicCamera(-80, 80, 45, -45, .1, 650);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = false; controls.minZoom = .7; controls.maxZoom = 5;
  controls.minPolarAngle = .001; controls.maxPolarAngle = Math.PI * .405;
  controls.rotateSpeed = .65; controls.zoomSpeed = .86; controls.panSpeed = .86;
  const cast = new THREE.Raycaster(), pointer = new THREE.Vector2(), projected = new THREE.Vector3();
  const homes = { relief: homeFraming(terrain.geometry, new THREE.Vector3(13,105,91)),
    flat: homeFraming(terrain.geometry, new THREE.Vector3(0,155,.02)) };
  let mode = 'relief', frame = 0, W = 1, H = 1;
  function draw() {
    frame = 0; renderer.render(scene, camera);
    events.project(position => {
      projected.copy(position).project(camera);
      return [(projected.x + 1) * W / 2, (1 - projected.y) * H / 2];
    }, controls.getAzimuthalAngle(), camera.zoom);
  }
  function invalidate() { if (!frame) frame = requestAnimationFrame(draw); }
  function size() {
    W = Math.max(1, host.clientWidth); H = Math.max(1, host.clientHeight);
    const aspect = W / H, span = Math.max(homes[mode].height, homes[mode].width / aspect);
    camera.left = -span * aspect / 2; camera.right = -camera.left; camera.top = span / 2; camera.bottom = -camera.top;
    camera.updateProjectionMatrix(); renderer.setSize(W, H); invalidate();
  }
  function reset(nextMode = mode) {
    mode = nextMode; controls.target.copy(homes[mode].center);
    camera.position.copy(controls.target).add(homes[mode].offset);
    controls.enableRotate = mode !== 'flat';
    controls.mouseButtons.LEFT = mode === 'flat' ? THREE.MOUSE.PAN : THREE.MOUSE.ROTATE;
    controls.touches.ONE = mode === 'flat' ? THREE.TOUCH.PAN : THREE.TOUCH.ROTATE;
    camera.zoom = 1; controls.update(); size();
  }
  function locate(e) {
    const rect = canvas.getBoundingClientRect();
    pointer.set((e.clientX - rect.left) / rect.width * 2 - 1, -(e.clientY - rect.top) / rect.height * 2 + 1);
    return pickTerrainRegion(cast, surfaces, camera, pointer);
  }
  const removePicking = bindPicking(canvas, locate, events);
  const observer = new ResizeObserver(size); observer.observe(host);
  controls.addEventListener('change', invalidate); reset();
  function lost(e) { e.preventDefault(); events.lost(); }
  canvas.addEventListener('webglcontextlost', lost);
  return {
    reset, setView: reset, invalidate,
    updateTexture() { texture.needsUpdate = true; invalidate(); },
    zoom(factor) { camera.zoom = THREE.MathUtils.clamp(camera.zoom * factor, controls.minZoom, controls.maxZoom); camera.updateProjectionMatrix(); invalidate(); },
    dispose() {
      observer.disconnect(); cancelAnimationFrame(frame); controls.removeEventListener('change', invalidate);
      removePicking(); controls.dispose(); canvas.removeEventListener('webglcontextlost', lost);
      const resources = new Set();
      scene.traverse(o => { if (o.isMesh) {
        resources.add(o.geometry); resources.add(o.material);
        if (o.material.map) resources.add(o.material.map);
        if (o.isInstancedMesh) o.dispose();
      } });
      resources.forEach(item => item.dispose()); renderer.dispose(); canvas.remove();
    }
  };
}
