import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { BookOpen, Box, Castle, Check, CircleHelp, Compass, Images, Landmark, Scan,
  Map as MapIcon, MapPin, Mountain, MountainSnow, Route, ScrollText, Ship, Sprout, Waves, X } from 'lucide-react';
import MapViewport from './地图视窗.jsx';
import { places, regions, placeById, regionById, routes } from './地理资料.js';
import trade from './图册/武元大陆舆图-山川与商路.png';
import journey from './图册/朔河州行程与界域示意.svg';
import harbors from './图册/七港泊位与隐城水脉.svg';
import './舆图.css';

const sheets = [
  { id: 'trade', name: '山川与商路', src: trade, note: '沿朔河读六处拟名，从北荒草甸、临川支流一直看到七港外礁。' },
  { id: 'journey', name: '朔河州行程', src: journey, note: '南渡仓是首卷的水陆分路处。下半图另列武元界内地底、地表海疆及界外通行条件。' },
  { id: 'harbors', name: '七港与隐城', src: harbors, note: '上图列出七港泊位与外礁候选线，下图独立展示分水室、高廊与地底旧城。地表井址待勘。' }
];
const regionIcons = { shuo: Waves, steppe: Sprout, west: Mountain, central: Landmark, east: MountainSnow, ports: Ship, sea: Waves, isles: Compass };

function AtlasDialog({ kind, sheetId, openSheet, close }) {
  const ref = useRef(null);
  const [originalSize, setOriginalSize] = useState(false);
  useEffect(() => {
    const dialog = ref.current;
    dialog.showModal();
    return () => dialog.close();
  }, []);
  const sheet = sheets.find(x => x.id === sheetId);
  return <dialog ref={ref} className={'atlas-dialog ' + (kind === 'help' ? 'help-dialog' : '')} aria-labelledby="dialog-title"
    onCancel={e => { e.preventDefault(); close(); }} onClick={e => { if (e.target === ref.current) close(); }}>
    <div className="dialog-inner">
      <div className="dialog-heading"><h2 id="dialog-title">{kind === 'help' ? '阅图说明' : '原图图集'}</h2><button className="icon-button" onClick={close} aria-label="关闭弹窗" autoFocus><X size={20}/></button></div>
      {kind === 'help' ? <div className="help-content">
        <h3>如何看图</h3>
        <p>点选任意一块地形或海面，即可查看区域图志。点地标读该地的故事，也可以从区域索引用键盘选择。</p>
        <p>立体视角中，拖动旋转，滚轮缩放，右键拖动平移。触屏上用单指旋转、双指缩放或平移。切到俯视后，单指可拖动地图。</p>
        <h3>图幅与时点</h3>
        <p>图取大周仍在、临川尚待授予试治的开篇时点。地貌、海岸、区域轮廓和点间距离均为拟绘。脚程见朔河州行程图。</p>
        <p>海疆与地底同属武元界。地底井址尚待勘定，井道另用一幅剖面图。卷末小渡场与临川旧渡各有其地。</p>
        <button className="paper-button" onClick={() => openSheet('journey')}><Images size={16}/>查阅行程附图</button>
      </div> : <>
        <div className="sheet-tabs" aria-label="选择原图">{sheets.map(s => <button key={s.id} aria-pressed={sheetId === s.id} onClick={() => { setOriginalSize(false); openSheet(s.id); }}>{s.name}</button>)}</div>
        <div className={'sheet-image' + (originalSize ? ' original-size' : '')} tabIndex={originalSize ? 0 : undefined}
          aria-label={originalSize ? '原尺寸图幅，可滚动查看' : undefined}><img key={sheet.id} src={sheet.src} alt={sheet.name} style={originalSize ? {width: sheet.id === 'journey' ? 1440 : sheet.id === 'harbors' ? 1520 : 1536} : undefined}/></div>
        <div className="sheet-caption"><p>{sheet.note}</p><button aria-pressed={originalSize} onClick={() => setOriginalSize(!originalSize)}><Scan size={14}/>{originalSize ? '适应窗口' : '查看原尺寸'}</button></div>
      </>}
    </div>
  </dialog>;
}

function Gazetteer({ region, place, pickPlace, back, openSheet }) {
  const item = place || region, list = places.filter(p => p.region === region.id);
  const links = place ? routes.filter(r => r.from === place.id || r.to === place.id) : [];
  const Illustration = regionIcons[region.id], sheet = sheets.find(s => s.id === region.sheet);
  const x = place ? place.at[0] * 100 : region.crop[0], y = place ? place.at[1] * 100 : region.crop[1];
  return <aside className="gazetteer" id="所选图志" tabIndex="-1" aria-label="所选区域图志">
    <div className="panel-heading"><div><BookOpen size={18}/><h2>{place ? '地标图志' : '区域图志'}</h2></div>{place && <button className="text-button" onClick={back}>返回{region.name}</button>}</div>
    <div className="detail-body">
      <div className="detail-kicker"><span className="ink-line"/>{place ? region.name + ' · ' + place.kind : region.kind}</div>
      <div className="detail-title"><h3 aria-live="polite">{item.name}</h3><Illustration size={28} strokeWidth={1.35}/></div>
      <div className="detail-art" role="img" aria-label={region.name + '，原舆图局部'}
        style={{ backgroundImage: 'url("' + trade + '")', backgroundPosition: Math.max(0, Math.min(100, (x - 12) / .76)) + '% ' + Math.max(0, Math.min(100, (y - 6) / .88)) + '%' }}/>
      <p className="detail-copy">{place ? place.info : region.summary}</p>
      {place ? <>
        <h4><MapPin size={15}/>点位依据</h4>
        <p className="note-copy">{place.draft ? '本版图志拟名，具体位置随卷内情节勘定。' : '地名与用途见作品设定，图上坐标按相对位置拟绘。'}</p>
        {links.length > 0 && <><h4><Route size={15}/>相关行程</h4><ul className="route-list">{links.map(r => <li key={r.id}><span>{placeById[r.from].name} 至 {placeById[r.to].name}</span><small>{r.time}</small></li>)}</ul></>}
      </> : <>
        {list.length > 0 && <><h4><MapPin size={15}/>区域地标</h4><div className="place-list">{list.map(p => <button key={p.id} onClick={() => pickPlace(p.id)}>{p.city ? <Castle size={13}/> : <MapPin size={13}/>} {p.name}</button>)}</div></>}
        <h4><Route size={15}/>通行记</h4><p className="note-copy">{region.passage}</p>
      </>}
    </div>
    <button className="sheet-link" onClick={() => openSheet(sheet.id)}><ScrollText size={16}/> 对照原图 <strong>{sheet.name}</strong></button>
  </aside>;
}

function App() {
  const [regionId, setRegion] = useState('shuo'), [placeId, setPlace] = useState(null);
  const [view, setView] = useState('relief'), [hasGL, setGL] = useState(true);
  const [dialog, setDialog] = useState(null), [sheetId, setSheet] = useState('trade');
  function pickRegion(id) { setRegion(id); setPlace(null); }
  function pickPlace(id) { setPlace(id); setRegion(placeById[id].region); }
  function openSheet(id) { setSheet(id); setDialog('gallery'); }
  const region = regionById[regionId];
  return <>
    <header className="masthead"><div className="topbar">
      <div className="brand"><span className="brand-seal"><MountainSnow size={24} strokeWidth={1.45}/></span><strong>山河图志</strong><i/><span className="book-name">我在异界打天下</span></div>
      <nav aria-label="读图工具"><button onClick={() => openSheet('trade')}><Images size={17}/><span>原图图集</span></button><button onClick={() => setDialog('help')} aria-label="阅图说明"><CircleHelp size={17}/><span>阅图说明</span></button></nav>
    </div></header>
    <main>
      <div className="page-heading"><div>
        <div className="eyebrow"><span/>大周开篇形势</div>
        <h1>武元大陆舆图</h1>
      </div>
      <div className="view-switch" aria-label="地图视角">
        <button disabled={!hasGL} aria-pressed={view === 'relief'} onClick={() => setView('relief')}><Box size={16}/>立体地形</button>
        <button aria-pressed={view === 'flat'} onClick={() => setView('flat')}><MapIcon size={16}/>俯视平面</button>
      </div></div>
      <div className="atlas-layout">
        <div className="map-column">
          <MapViewport regionId={regionId} placeId={placeId} pickRegion={pickRegion} pickPlace={pickPlace} view={view} fallback={() => { setGL(false); setView('flat'); }}/>
          <section className="region-index" aria-label="区域索引">
            <div className="index-heading"><div><Compass size={18}/><h2>区域索引</h2></div><span>{regions.length} 个区域</span></div>
            <div className="region-grid">{regions.map(r => <button key={r.id} className={r.id === regionId ? 'active' : ''}
              aria-pressed={r.id === regionId} onClick={() => pickRegion(r.id)}><i style={{ background: r.color }}/>{r.name}{r.id === regionId && <Check size={14}/>}</button>)}</div>
          </section>
        </div>
        <Gazetteer region={region} place={placeById[placeId]} pickPlace={pickPlace} back={() => setPlace(null)} openSheet={openSheet}/>
      </div>
      <footer><span>《我在异界打天下》作者用图</span><span>地貌、点位与区域轮廓均为拟绘</span></footer>
    </main>
    {dialog && <AtlasDialog kind={dialog} sheetId={sheetId} openSheet={openSheet} close={() => setDialog(null)}/>}
  </>;
}

createRoot(document.getElementById('root')).render(<App/>);
