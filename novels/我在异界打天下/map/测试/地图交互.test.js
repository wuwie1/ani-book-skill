import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { Mesh, MeshBasicMaterial, OrthographicCamera, Raycaster, Vector2, Vector3 } from 'three';
import { regions, regionById, places, placeById, routes } from '../地理资料.js';
import { regionAt, getField, sampleHeight, worldAt } from '../地形.js';
import { bindPicking, makeTerrainGeometry, pickTerrainRegion } from '../立体场景.js';

test('图幅内的采样点及四边都有图志，图框外不误选', () => {
  const found = new Set();
  for (let y = 0; y <= 200; y++) {
    for (let x = 0; x <= 300; x++) {
      const id = regionAt(x / 300, y / 200);
      assert.ok(regionById[id]?.summary);
      found.add(id);
    }
  }
  assert.deepEqual(found, new Set(regions.map(r => r.id)));
  for (const pair of [[1.01,.5],[.5,-.01],[NaN,0],[0,Infinity]]) assert.equal(regionAt(...pair), null);
});

test('地标、七港与行程归属正确，陆海高程有别', () => {
  for (const area of regions) assert.equal(regionAt(...area.anchor), area.id);
  for (const p of places) assert.equal(regionAt(...p.at), p.region, p.name);
  assert.equal(places.filter(p => p.region === 'ports').length, 7);
  assert.equal(placeById.wind.region, 'isles');
  assert.deepEqual(routes.slice(0, 3).map(r => [r.from,r.to,r.time]), [
    ['jing','depot','约一时辰'], ['depot','post','陆路一日'], ['depot','ferry','顺水约半日']
  ]);
  for (const r of routes) assert.ok(placeById[r.from] && placeById[r.to]);
  assert.ok(getField().every(Number.isFinite));
  assert.ok(sampleHeight(.9,.75) < 0 && sampleHeight(...placeById.wind.at) > 0);
  assert.ok(Math.max(...getField()) > 10);
});

test('地形射线在倾斜、旋转、平移、缩放和俯视后均能选中八区的非标签位置', () => {
  const terrain = new Mesh(makeTerrainGeometry(), new MeshBasicMaterial());
  terrain.updateMatrixWorld();
  const cast = new Raycaster(), xy = new Vector2();
  const sites = { shuo: [.51,.445], west: [.145,.47], steppe: [.55,.098], central: [.385,.79],
    east: [.802,.44], ports: [.734,.681], sea: [.731,.858], isles: [.903,.863] };
  for (const [p, target, zoom] of [
    [[13,105,91],[0,1.7,0],1], [[-31,120,50],[3,1,-2],1.24], [[0,155,.02],[0,0,0],1.08]
  ]) {
    const camera = new OrthographicCamera(-97,97,61,-61,.1,650);
    camera.position.fromArray(p); camera.lookAt(new Vector3(...target)); camera.zoom = zoom;
    camera.updateProjectionMatrix(); camera.updateMatrixWorld();
    for (const [id, uv] of Object.entries(sites)) {
      const pos = worldAt(uv).project(camera);
      assert.equal(pickTerrainRegion(cast, [terrain], camera, xy.set(pos.x, pos.y)), id, id);
    }
    assert.equal(pickTerrainRegion(cast, [terrain], camera, xy.set(-1, 1)), null);
  }
  terrain.geometry.dispose(); terrain.material.dispose();
});

test('轻点命中，拖走再返回、右击、取消和双指手势均不改变选区', () => {
  const canvas = new EventTarget(), picks = [];
  const stop = bindPicking(canvas, () => 'sea', { pick: id => picks.push(id), hover() {} });
  function pointer(type, id, x, button = 0) {
    const event = new Event(type);
    Object.assign(event, { pointerId: id, pointerType: 'touch', clientX: x, clientY: 20, button });
    canvas.dispatchEvent(event);
  }
  pointer('pointerdown', 1, 2); pointer('pointerup', 1, 3);
  pointer('pointerdown', 2, 2); pointer('pointermove', 2, 23); pointer('pointerup', 2, 2);
  pointer('pointerdown', 3, 2, 2); pointer('pointerup', 3, 2, 2);
  pointer('pointerdown', 4, 2); pointer('pointercancel', 4, 2); pointer('pointerup', 4, 2);
  pointer('pointerdown', 5, 2); pointer('pointerdown', 6, 90); pointer('pointerup', 6, 90); pointer('pointerup', 5, 2);
  stop(); pointer('pointerdown', 7, 2); pointer('pointerup', 7, 2);
  assert.deepEqual(picks, ['sea']);
});

test('离线成品内嵌程序、样式及现行图册的三份原图', async () => {
  const page = await readFile(new URL('../离线地图/index.html', import.meta.url), 'utf8');
  assert.ok(!/<script\b[^>]*\bsrc\s*=|<link\b[^>]*\brel=["'](?:stylesheet|modulepreload)["']/i.test(page));
  assert.ok(page.includes('<style') && page.includes('Lucide Contributors'));
  for (const name of ['武元大陆舆图-山川与商路.png', '朔河州行程与界域示意.svg', '七港泊位与隐城水脉.svg']) {
    const bytes = await readFile(new URL('../图册/' + name, import.meta.url));
    assert.ok(page.includes(bytes.toString('base64')), name);
  }
});
