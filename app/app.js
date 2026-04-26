// Contextos Geológicos — app principal
// Stack: Leaflet vanilla, sin build. Datos en /app/data/*.

const state = {
  contextos: null,
  chileContextos: null,      // 22 contextos Mourgues mapeados al mapa al millón (lazy)
  antartica: null,           // 9 SCAR Frameworks (lazy)
  chileGeologico: null,      // Mapa geológico de Chile 1:1M crudo (lazy, capa base)
  lexico: null,
  layer: null,               // capa de contextos (CGT)
  baseLayer: null,           // capa base geológica
  selectedId: null,
  filterRegion: 'chile',
  filterTypes: new Set(),
  filterAges: new Set(),
  showBase: true,
  showGeositios: true,
  geositios: null,
  map: null,
};

const REGION_VIEW = {
  chile: { center: [-46, -73], zoom: 5 },
  antartica: { center: [-90, 0], zoom: 2 },
};

// EPSG:3031 — Antarctic Polar Stereographic (true scale at 71°S)
// Resolutions and origin tomados de la convención del SCAR Antarctic Digital Database.
const ANTARCTIC_CRS_BOUNDS = 12367396.2185;
const antarcticCRS = () => new L.Proj.CRS(
  'EPSG:3031',
  '+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs',
  {
    origin: [-ANTARCTIC_CRS_BOUNDS, ANTARCTIC_CRS_BOUNDS],
    resolutions: [
      67733.46880027094,
      33866.73440013547,
      16933.367200067736,
      8466.683600033868,
      4233.341800016934,
      2116.670900008467,
      1058.3354500042335,
      529.1677250021168,
      264.5838625010584,
    ],
  }
);

// Helper: create element with optional class, text, and children
function el(tag, opts = {}, children = []) {
  const node = document.createElement(tag);
  if (opts.className) node.className = opts.className;
  if (opts.text != null) node.textContent = opts.text;
  if (opts.title) node.title = opts.title;
  if (opts.dataset) Object.assign(node.dataset, opts.dataset);
  if (opts.style) Object.assign(node.style, opts.style);
  children.forEach(c => node.appendChild(c));
  return node;
}

function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }

// ---------- Tabs ----------
document.querySelectorAll('.tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    if (btn.dataset.tab === 'mapa' && state.map) {
      setTimeout(() => state.map.invalidateSize(), 50);
    }
    if (btn.dataset.tab === 'globo' && typeof window.initGlobo === 'function') {
      window.initGlobo();
    }
  });
});

// ---------- Mapa ----------
// Web Mercator (default): para Chile/mundo. Polar Stereographic: para Antártica.
function initMap(region = 'chile') {
  if (state.map) {
    state.map.remove();
    state.map = null;
  }

  if (region === 'antartica') {
    const map = L.map('map', {
      crs: antarcticCRS(),
      center: REGION_VIEW.antartica.center,
      zoom: REGION_VIEW.antartica.zoom,
      minZoom: 0,
      maxZoom: 8,
      attributionControl: true,
    });
    // Imagery polar: NASA GIBS BlueMarble (relieve sombreado, EPSG:3031, sin auth)
    L.tileLayer.wms('https://gibs.earthdata.nasa.gov/wms/epsg3031/best/wms.cgi', {
      layers: 'BlueMarble_ShadedRelief_Bathymetry',
      format: 'image/jpeg',
      transparent: false,
      attribution: 'NASA GIBS / Blue Marble',
    }).addTo(map);
    map.attributionControl.addAttribution('SCAR/GNS GeoMAP v2022.08 (Cox et al. 2023)');
    state.map = map;
  } else {
    const map = L.map('map', {
      center: REGION_VIEW.chile.center,
      zoom: REGION_VIEW.chile.zoom,
      minZoom: 2,
    });
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      subdomains: 'abcd',
      maxZoom: 19,
    }).addTo(map);
    state.map = map;
  }
}

function styleFor(feature) {
  // Para Chile, los CGT son rectángulos placeholder — los pinto como contornos
  // semi-transparentes para que se vea el mapa geológico de fondo.
  const isChile = feature.properties.region === 'chile';
  return {
    color: feature.properties.color,
    weight: isChile ? 2 : 1,
    fillColor: feature.properties.color,
    fillOpacity: isChile ? 0.18 : 0.5,
    dashArray: isChile ? '4,3' : null,
  };
}

async function ensureAntarticaLoaded() {
  if (state.antartica) return;
  try {
    // Por defecto: 9 SCAR Frameworks (interpretativos). Si querés ver las 21 SIMPCODE, cambia a antartica_simplecode.geojson.
    state.antartica = await fetch('data/antartica_frameworks.geojson').then(r => r.json());
  } catch (e) {
    console.warn('No se pudo cargar antartica_frameworks.geojson, fallback a SIMPCODE', e);
    try {
      state.antartica = await fetch('data/antartica_simplecode.geojson').then(r => r.json());
    } catch (e2) {
      state.antartica = { type: 'FeatureCollection', features: [] };
    }
  }
}

async function ensureChileGeologicoLoaded() {
  if (state.chileGeologico) return;
  try {
    state.chileGeologico = await fetch('data/chile_geologico.geojson').then(r => r.json());
  } catch (e) {
    console.warn('No se pudo cargar chile_geologico.geojson — corre scripts/build_chile_geologico.py', e);
    state.chileGeologico = { type: 'FeatureCollection', features: [] };
  }
}

let geositiosLayer = null;
async function ensureGeositiosLoaded() {
  if (state.geositios) return;
  try {
    state.geositios = await fetch('data/geositios_inventario_nacional.geojson').then(r => r.json());
  } catch (e) {
    console.warn('Inventario Nacional no disponible', e);
    state.geositios = { type: 'FeatureCollection', features: [] };
  }
}

async function renderGeositiosLayer() {
  if (geositiosLayer) {
    state.map.removeLayer(geositiosLayer);
    geositiosLayer = null;
  }
  if (!state.showGeositios || state.filterRegion !== 'chile') return;
  await ensureGeositiosLoaded();
  geositiosLayer = L.geoJSON(state.geositios, {
    pointToLayer: (feature, latlng) => {
      const escala = (feature.properties['ESCALA DE RELEVANCIA'] || '').toLowerCase();
      let color = '#fff';
      if (escala.includes('internacional')) color = '#e74c3c';
      else if (escala.includes('nacional')) color = '#f39c12';
      else if (escala.includes('regional')) color = '#3498db';
      else color = '#95a5a6';
      return L.circleMarker(latlng, { radius: 7, color: '#000', weight: 1, fillColor: color, fillOpacity: 0.95 });
    },
    onEachFeature: (feature, layer) => {
      const p = feature.properties;
      const codigo = p['CÓDIGO INVENTARIO NACIONAL'] || '';
      const region = p['REGIÓN'] || '';
      const interes = p['INTERÉS GEOCIENTÍFICO PRINCIPAL'] || '';
      const escala = p['ESCALA DE RELEVANCIA'] || '';
      layer.bindPopup(
        `<strong>${p.nombre}</strong><br>` +
        `<span style="color:#888;font-size:0.8em">${codigo} · ${region}</span><br>` +
        `<em>${interes}</em><br>` +
        `<small>Relevancia: ${escala}</small><br>` +
        `<details><summary>Más info</summary>${(p.descripcion || '').slice(0, 400)}…</details>`
      );
    },
  }).addTo(state.map);
}

function styleBaseChile(feature) {
  return {
    color: feature.properties.color,
    weight: 0.4,
    fillColor: feature.properties.color,
    fillOpacity: 0.75,
    interactive: false,
  };
}

async function renderBaseLayer() {
  if (state.baseLayer) {
    state.map.removeLayer(state.baseLayer);
    state.baseLayer = null;
  }
  if (!state.showBase) return;

  if (state.filterRegion === 'chile') {
    await ensureChileGeologicoLoaded();
    state.baseLayer = L.geoJSON(state.chileGeologico, {
      style: styleBaseChile,
      interactive: false,
    });
    state.baseLayer.addTo(state.map);
    state.baseLayer.bringToBack();
  }
  // Antártica: por ahora sin base geológica detallada (los polígonos SIMPCODE ya cubren todo).
}

async function renderContextos() {
  // Si el CRS actual no coincide con la región pedida, recreo el mapa (incluyendo capa base).
  const wantPolar = state.filterRegion === 'antartica';
  const isPolar = state.map && state.map.options.crs && state.map.options.crs.code === 'EPSG:3031';
  if (!state.map || wantPolar !== isPolar) {
    initMap(state.filterRegion);
    state.baseLayer = null;
  } else if (state.layer) {
    state.map.removeLayer(state.layer);
  }
  await renderBaseLayer();
  await renderGeositiosLayer();

  let source;
  if (state.filterRegion === 'antartica') {
    await ensureAntarticaLoaded();
    source = state.antartica.features;
  } else {
    // Modo Chile: 22 contextos Mourgues mapeados desde el mapa al millón.
    // Fallback: contextos.geojson (19 CGT Aysén) si chile_contextos no carga.
    try {
      if (!state.chileContextos) {
        state.chileContextos = await fetch('data/chile_contextos.geojson').then(r => r.json());
      }
      source = state.chileContextos.features;
    } catch (e) {
      console.warn('chile_contextos.geojson no disponible, fallback a Aysén CGT', e);
      source = state.contextos.features.filter(f => f.properties.region === 'chile');
    }
  }

  const features = source.filter(f => {
    const p = f.properties;
    if (state.filterTypes.size && !state.filterTypes.has(p.tipo)) return false;
    if (state.filterAges.size && !state.filterAges.has(p.edad)) return false;
    return true;
  });

  state.layer = L.geoJSON({ type: 'FeatureCollection', features }, {
    style: styleFor,
    onEachFeature: (feature, layer) => {
      layer.on('click', () => showDetail(feature.properties));
      layer.on('mouseover', () => layer.setStyle({ weight: 3, fillOpacity: 0.65 }));
      layer.on('mouseout', () => layer.setStyle({ weight: 1.5, fillOpacity: 0.45 }));
      layer.bindTooltip(feature.properties.nombre, { sticky: true });
    },
  }).addTo(state.map);

  if (features.length) {
    if (state.filterRegion === 'antartica') {
      state.map.setView(REGION_VIEW.antartica.center, REGION_VIEW.antartica.zoom);
    } else {
      state.map.fitBounds(state.layer.getBounds(), { padding: [40, 40], maxZoom: 6 });
    }
  }

  // Reconstruir filtros según la región actual (las clases cambian)
  rebuildFilters(source);
  renderContextList(features);
}

function rebuildFilters(features) {
  const types = [...new Set(features.map(f => f.properties.tipo))].filter(Boolean).sort();
  const ages = [...new Set(features.map(f => f.properties.edad))].filter(Boolean).sort();
  // Si los filtros activos no aplican a la región nueva, los limpiamos
  for (const t of [...state.filterTypes]) if (!types.includes(t)) state.filterTypes.delete(t);
  for (const a of [...state.filterAges]) if (!ages.includes(a)) state.filterAges.delete(a);
  buildChipGroup('type-filters', types, state.filterTypes);
  buildChipGroup('age-filters', ages, state.filterAges);
}

function renderContextList(features) {
  const ul = document.getElementById('context-list');
  clear(ul);
  features.forEach(f => {
    const swatch = el('span', { className: 'swatch', style: { background: f.properties.color } });
    const li = el('li', {}, [swatch]);
    li.appendChild(document.createTextNode(f.properties.nombre));
    li.addEventListener('click', () => {
      showDetail(f.properties);
      const layerForFeature = findLayerById(f.properties.id);
      if (layerForFeature) state.map.fitBounds(layerForFeature.getBounds(), { padding: [60, 60], maxZoom: 7 });
    });
    ul.appendChild(li);
  });
}

function findLayerById(id) {
  let found = null;
  state.layer.eachLayer(l => { if (l.feature.properties.id === id) found = l; });
  return found;
}

function showDetail(p) {
  const panel = document.getElementById('detail-panel');
  panel.classList.remove('hidden');
  document.getElementById('tab-mapa').classList.add('with-detail');
  setTimeout(() => state.map.invalidateSize(), 50);

  document.getElementById('detail-name').textContent = p.nombre;

  const badges = document.getElementById('detail-badges');
  clear(badges);
  badges.appendChild(el('span', { text: p.tipo, style: { background: p.color, color: '#fff' } }));
  badges.appendChild(el('span', { text: p.edad }));
  badges.appendChild(el('span', { text: p.region === 'chile' ? '🇨🇱 Chile' : '❄ Antártica' }));

  document.getElementById('detail-desc').textContent = p.descripcion || '—';
  document.getElementById('detail-age').textContent = p.edad;

  const ul = document.getElementById('detail-units');
  clear(ul);
  (p.unidades || []).forEach(u => {
    const li = el('li', { text: u });
    const match = state.lexico?.entries.find(e => e.nombre === u);
    if (match) {
      li.style.cursor = 'pointer';
      li.style.color = 'var(--accent-2)';
      li.title = 'Ver en léxico';
      li.addEventListener('click', () => {
        document.querySelector('.tab[data-tab="lexico"]').click();
        renderLexEntry(match);
        document.querySelectorAll('#lex-list li').forEach(x => x.classList.toggle('active', x.dataset.id === match.id));
      });
    }
    ul.appendChild(li);
  });
}

document.querySelector('.detail-panel .close').addEventListener('click', () => {
  document.getElementById('detail-panel').classList.add('hidden');
  document.getElementById('tab-mapa').classList.remove('with-detail');
  setTimeout(() => state.map.invalidateSize(), 50);
});

// ---------- Filtros ----------
function buildChipGroup(containerId, values, set) {
  const container = document.getElementById(containerId);
  clear(container);
  values.forEach(v => {
    const chip = el('span', { className: 'chip', text: v });
    chip.addEventListener('click', () => {
      if (set.has(v)) { set.delete(v); chip.classList.remove('active'); }
      else { set.add(v); chip.classList.add('active'); }
      renderContextos();
    });
    container.appendChild(chip);
  });
}

document.getElementById('region-filter').addEventListener('change', e => {
  state.filterRegion = e.target.value;
  renderContextos();
});

document.getElementById('toggle-base').addEventListener('change', e => {
  state.showBase = e.target.checked;
  renderBaseLayer();
});

document.getElementById('toggle-geositios').addEventListener('change', e => {
  state.showGeositios = e.target.checked;
  renderGeositiosLayer();
});

// ---------- Léxico ----------
function renderLexList() {
  const list = document.getElementById('lex-list');
  const q = document.getElementById('lex-search').value.toLowerCase();
  const period = document.getElementById('lex-period').value;
  clear(list);
  state.lexico.entries
    .filter(e => !q || e.nombre.toLowerCase().includes(q) || (e.litologia || '').toLowerCase().includes(q))
    .filter(e => !period || e.periodo === period)
    .forEach(entry => {
      const title = el('div', { text: entry.nombre });
      const meta = el('div', { className: 'lex-meta', text: `${entry.rango} · ${entry.periodo}` });
      const li = el('li', { dataset: { id: entry.id } }, [title, meta]);
      li.addEventListener('click', () => {
        document.querySelectorAll('#lex-list li').forEach(x => x.classList.remove('active'));
        li.classList.add('active');
        renderLexEntry(entry);
      });
      list.appendChild(li);
    });
}

function renderLexEntry(e) {
  const detail = document.getElementById('lex-detail');
  clear(detail);
  detail.appendChild(el('h2', { text: e.nombre }));
  detail.appendChild(el('p', { className: 'muted', text: `${e.rango} · ${e.edad}` }));

  const dl = el('dl');
  const rows = [
    ['Litología', e.litologia],
    ['Distribución', e.distribucion],
    ['Espesor', e.espesor],
    ['Definición original', e.definicion],
  ];
  rows.forEach(([k, v]) => {
    if (!v) return;
    dl.appendChild(el('dt', { text: k }));
    dl.appendChild(el('dd', { text: v }));
  });

  const ctx = state.contextos?.features.find(f => f.properties.id === e.contexto);
  if (ctx) {
    dl.appendChild(el('dt', { text: 'Contexto geológico' }));
    const link = el('a', { text: ctx.properties.nombre });
    link.href = '#';
    link.style.color = 'var(--accent-2)';
    link.addEventListener('click', ev => {
      ev.preventDefault();
      document.querySelector('.tab[data-tab="mapa"]').click();
      document.getElementById('region-filter').value = ctx.properties.region;
      state.filterRegion = ctx.properties.region;
      renderContextos();
      setTimeout(() => showDetail(ctx.properties), 100);
    });
    dl.appendChild(el('dd', {}, [link]));
  }
  detail.appendChild(dl);
}

document.getElementById('lex-search').addEventListener('input', renderLexList);

function buildLexFilters() {
  const periods = [...new Set(state.lexico.entries.map(e => e.periodo))].sort();
  const sel = document.getElementById('lex-period');
  periods.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p; opt.textContent = p;
    sel.appendChild(opt);
  });
  sel.addEventListener('change', renderLexList);
}

// ---------- Bootstrap ----------
async function main() {
  initMap(state.filterRegion);
  const [ctxRes, lexRes] = await Promise.all([
    fetch('data/contextos.geojson').then(r => r.json()),
    fetch('data/lexico.json').then(r => r.json()),
  ]);
  state.contextos = ctxRes;
  state.lexico = lexRes;
  buildLexFilters();
  await renderContextos();
  renderLexList();
}

main().catch(err => {
  console.error(err);
  alert('Error cargando datos: ' + err.message + '\nLa app necesita servirse desde un servidor (no abrir como file://). Ejecuta:\n  python -m http.server 8000\nen la carpeta /app y abre http://localhost:8000');
});
