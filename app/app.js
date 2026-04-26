// Contextos Geológicos — app principal
// Stack: Leaflet vanilla, sin build. Datos en /app/data/*.

const state = {
  contextos: null,           // 19 CGT Chile (Aysén) + Antártica placeholders
  antartica: null,           // 21 SIMPLECODE classes from SCAR/GNS GeoMAP (lazy load)
  lexico: null,
  layer: null,
  selectedId: null,
  filterRegion: 'chile',
  filterTypes: new Set(),
  filterAges: new Set(),
  map: null,
};

const REGION_VIEW = {
  chile: { center: [-46, -73], zoom: 5 },
  antartica: { center: [-82, 0], zoom: 2 },
};

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
  });
});

// ---------- Mapa ----------
function initMap() {
  const map = L.map('map', { center: [-35, -71], zoom: 4, minZoom: 2 });
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(map);
  state.map = map;
}

function styleFor(feature) {
  return {
    color: feature.properties.color,
    weight: 1.5,
    fillColor: feature.properties.color,
    fillOpacity: 0.45,
  };
}

async function ensureAntarticaLoaded() {
  if (state.antartica) return;
  try {
    state.antartica = await fetch('data/antartica_simplecode.geojson').then(r => r.json());
  } catch (e) {
    console.warn('No se pudo cargar antartica_simplecode.geojson — corre scripts/build_antartica_geojson.py', e);
    state.antartica = { type: 'FeatureCollection', features: [] };
  }
}

async function renderContextos() {
  if (state.layer) state.map.removeLayer(state.layer);

  let source;
  if (state.filterRegion === 'antartica') {
    await ensureAntarticaLoaded();
    source = state.antartica.features;
  } else {
    source = state.contextos.features.filter(f => f.properties.region === 'chile');
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
  initMap();
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
