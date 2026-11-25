import React, { useEffect, useRef, useState } from 'react';
import { Check, Expand, Layers3, Minus, Plus, RotateCcw, Shrink, MousePointer2 } from 'lucide-react';
import { regions, places, regionById, placeById } from './地理资料.js';
import { worldAt } from './地形.js';
import { paintMap } from './地表绘制.js';

const markers = [
  ...regions.map(r => ({ id: r.id, name: r.name, area: true, position: worldAt(r.anchor, .5) })),
  ...places.map(p => ({ ...p, position: worldAt(p.at, p.city ? 1.5 : .6) }))
];

function positionLabels(elements, state, project, scale, w, h) {
  const occupied = [];
  function rank(m) {
    if (m.id === state.placeId) return 0;
    if (m.id === state.regionId) return 1;
    if (m.area) return 2;
    return m.major ? 3 : 4;
  }
  for (const m of [...markers].sort((a, b) => rank(a) - rank(b))) {
    const node = elements.get(m.id);
    if (!node) continue;
    let visible = state.showLabels && (m.area || m.major || m.id === state.placeId || (m.region === state.regionId && scale > 1.45));
    if (visible) {
      const [x, y] = project(m.position);
      const half = m.name.length * (m.area ? 8 : 6.5) + (m.id === state.regionId ? 14 : 6);
      const rect = { l: x - half, r: x + half, t: y - 22, b: y + 4 };
      visible = rect.r < w - 3 && rect.l > 3 && rect.b < h - 2 && rect.t > 2
        && !occupied.some(o => o.l < rect.r + 2 && o.r > rect.l - 2 && o.t < rect.b && o.b > rect.t);
      if (visible) {
        occupied.push(rect);
        node.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0) translate(-50%,-100%)';
      }
    }
    node.hidden = !visible;
  }
}

export default function MapViewport({ regionId, placeId, pickRegion, pickPlace, view, fallback }) {
  const host = useRef(null), compass = useRef(null), labelNodes = useRef(new Map());
  const controller = useRef(null), texture = useRef(null), latest = useRef(null), layerButton = useRef(null);
  const [hovered, hover] = useState(null), [showRoutes, setRoutes] = useState(true), [showLabels, setLabels] = useState(true);
  const [layers, setLayers] = useState(false), [full, setFull] = useState(false), [stage, setStage] = useState('loading');
  latest.current = { regionId, placeId, pickRegion, view, fallback, showLabels, showRoutes, hovered };

  useEffect(() => {
    let alive = true, fallbackFrame = 0;
    const surface = document.createElement('canvas');
    paintMap(surface, latest.current); texture.current = surface;
    const events = {
      hover, pick: id => latest.current.pickRegion(id),
      project(project, angle, scale) {
        if (!host.current) return;
        positionLabels(labelNodes.current, latest.current, project, scale, host.current.clientWidth, host.current.clientHeight);
        if (compass.current) compass.current.style.transform = 'rotate(' + angle + 'rad)';
      },
      lost() { fallbackFrame = requestAnimationFrame(useFlat); }
    };
    async function useFlat() {
      if (!alive) return;
      controller.current?.dispose(); controller.current = null;
      const { createFlatScene } = await import('./平面场景.js');
      if (!alive) return;
      controller.current = createFlatScene(host.current, surface, events);
      latest.current.fallback(); setStage('flat');
    }
    import('./立体场景.js').then(({ createScene }) => {
      if (!alive) return;
      try {
        controller.current = createScene(host.current, surface, events);
        if (latest.current.view !== 'relief') controller.current.setView(latest.current.view);
        setStage('ready');
      } catch { useFlat(); }
    });
    return () => {
      alive = false; cancelAnimationFrame(fallbackFrame); controller.current?.dispose(); controller.current = null;
    };
  }, []);
  useEffect(() => {
    if (texture.current) { paintMap(texture.current, latest.current); controller.current?.updateTexture(); }
  }, [regionId, hovered, showRoutes]);
  useEffect(() => { controller.current?.invalidate(); }, [showLabels, placeId]);
  useEffect(() => { controller.current?.setView(view); }, [view]);
  useEffect(() => {
    if (!layers) return;
    function dismiss(e) { if (!e.target.closest('.layer-menu')) setLayers(false); }
    function escape(e) { if (e.key === 'Escape') { setLayers(false); layerButton.current?.focus(); } }
    document.addEventListener('pointerdown', dismiss); document.addEventListener('keydown', escape);
    return () => { document.removeEventListener('pointerdown', dismiss); document.removeEventListener('keydown', escape); };
  }, [layers]);
  useEffect(() => {
    if (!full) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    function escape(e) { if (e.key === 'Escape') setFull(false); }
    document.addEventListener('keydown', escape);
    return () => { document.body.style.overflow = previous; document.removeEventListener('keydown', escape); };
  }, [full]);

  const selected = placeById[placeId] || regionById[regionId];
  return <section className={'map-frame' + (full ? ' expanded' : '')} aria-label="交互地图">
    <div className={'map-stage' + (hovered ? ' over-area' : '')}>
      <div className="render-host" ref={host} />
      <div className="pin-layer">
        {markers.map(m => <button key={m.id} type="button" hidden
          ref={node => { if (node) labelNodes.current.set(m.id, node); else labelNodes.current.delete(m.id); }}
          className={'map-pin ' + (m.area ? 'area-pin' : 'place-pin') + (m.id === regionId || m.id === placeId ? ' selected' : '') + (['sea','isles'].includes(m.id) ? ' water-pin' : '')}
          aria-label={'在地图上选择' + m.name} onClick={() => m.area ? pickRegion(m.id) : pickPlace(m.id)}>{m.name}</button>)}
      </div>
      <div className="layer-menu">
        <button ref={layerButton} className="map-tool layer-trigger" aria-expanded={layers} onClick={() => setLayers(!layers)}><Layers3 size={16}/>图层</button>
        {layers && <div className="layer-options">
          {[[showLabels, setLabels, '地名标注'], [showRoutes, setRoutes, '水陆商路']].map(([checked, change, name]) =>
            <label key={name}><input type="checkbox" checked={checked} onChange={e => change(e.target.checked)}/><span className="tick">{checked && <Check size={13}/>}</span>{name}</label>)}
        </div>}
      </div>
      <div className="compass" aria-label="北向指针"><div ref={compass} className="compass-dial"><b>北</b><i/><em/></div></div>
      <div className="zoom-tools">
        <button className="map-tool" aria-label="放大地图" title="放大" onClick={() => controller.current?.zoom(1.28)}><Plus size={17}/></button>
        <button className="map-tool" aria-label="缩小地图" title="缩小" onClick={() => controller.current?.zoom(1 / 1.28)}><Minus size={17}/></button>
        <button className="map-tool" aria-label="复位视角" title="复位视角" onClick={() => controller.current?.reset()}><RotateCcw size={15}/></button>
      </div>
      <div className="map-readout" aria-hidden="true"><MousePointer2 size={13}/>{hovered ? regionById[hovered].name : '点选地形查阅图志'}</div>
      {full && <div className="full-detail" aria-live="polite"><strong>{selected.name}</strong><p>{selected.info || selected.summary}</p></div>}
      {stage === 'loading' && <div className="map-loading" role="status">正在展开舆图…</div>}
    </div>
    <div className="map-caption"><div className="legend" aria-label="图例">
      <span><i className="legend-city"/>城邑</span><span><i className="legend-river"/>水系</span>{showRoutes && <span><i className="legend-route"/>商路</span>}
    </div>{!full && <a className="mobile-detail" href="#所选图志">{selected.name}图志</a>}
      <span className="gesture-tip">{stage === 'flat' ? '当前设备使用平面图' : view === 'flat' ? '拖动平移 · 滚轮缩放' : '拖动旋转 · 滚轮缩放'}</span>
      <button className="expand-button" aria-pressed={full} aria-label={full ? '收起地图' : '展开地图'} onClick={() => setFull(!full)}>{full ? <Shrink size={16}/> : <Expand size={16}/>}<span>{full ? '收起' : '展开'}</span></button>
    </div>
  </section>;
}
