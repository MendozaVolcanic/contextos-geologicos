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
  // Antártica
  antarticaMode: 'frameworks',       // 'frameworks' | 'simplecode'
  antarticaSimplecode: null,         // 21 SIMPCODE GeoMAP (lazy)
  antarticGeositios: null,           // ASPAs + SCAR/IUGS geosites (lazy)
  showAntarticGeositios: true,
  showAntarticHeatmap: false,        // heatmap densidad publicaciones
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
    if (btn.dataset.tab === 'bedmap') {
      initBedmap();
    }
    if (btn.dataset.tab === 'stats') {
      initStats();
    }
  });
});

// ---------- Stats (Bibliometría SCAR) ----------
let statsInitialized = false;
async function initStats() {
  if (statsInitialized) return;
  statsInitialized = true;
  try {
    const prop = await fetch('data/antartica_geositios_propuestos.geojson')
      .then(r => r.json());
    const feats = prop.features || [];
    if (!feats.length) {
      document.getElementById('stats-summary').textContent = 'Sin datos. Corre el pipeline primero.';
      return;
    }

    // ---- Resumen ----
    const totalPubs = feats.reduce((s, f) => s + (f.properties.pubs_count || 0), 0);
    const totalHits = feats.reduce((s, f) => s + (f.properties.hits_count || 0), 0);
    const totalWS = feats.reduce((s, f) => s + (f.properties.weighted_score || 0), 0);
    document.getElementById('stats-summary').innerHTML =
      `<strong>${feats.length}</strong> candidatos<br>` +
      `<strong>${totalPubs}</strong> doc-mencion total<br>` +
      `<strong>${totalHits}</strong> menciones brutas<br>` +
      `<strong>${totalWS.toFixed(0)}</strong> weighted_score acumulado`;

    // ---- Chart 1: Distribución por framework ----
    const byFW = {};
    feats.forEach(f => {
      const fw = f.properties.framework || '(sin asignar)';
      byFW[fw] = (byFW[fw] || 0) + 1;
    });
    const fwSorted = Object.entries(byFW).sort((a, b) => b[1] - a[1]);
    new Chart(document.getElementById('chart-frameworks').getContext('2d'), {
      type: 'bar',
      data: {
        labels: fwSorted.map(([k]) => k.length > 35 ? k.slice(0, 32) + '…' : k),
        datasets: [{
          label: 'Candidatos',
          data: fwSorted.map(([, v]) => v),
          backgroundColor: '#5fb878',
          borderColor: '#3a8c52',
          borderWidth: 1,
        }],
      },
      options: {
        indexAxis: 'y',
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, ticks: { color: '#e6edf3' }, grid: { color: '#30363d' } },
          y: { ticks: { color: '#e6edf3', font: { size: 11 } }, grid: { color: '#30363d' } },
        },
      },
    });

    // ---- Chart 2: Top 20 por weighted_score ----
    const top20 = [...feats]
      .sort((a, b) => (b.properties.weighted_score || 0) - (a.properties.weighted_score || 0))
      .slice(0, 20);
    new Chart(document.getElementById('chart-top-sites').getContext('2d'), {
      type: 'bar',
      data: {
        labels: top20.map(f => f.properties.nombre),
        datasets: [
          {
            label: 'Weighted score',
            data: top20.map(f => f.properties.weighted_score || 0),
            backgroundColor: '#d9764a',
            borderColor: '#b85e36',
            borderWidth: 1,
            yAxisID: 'y',
          },
          {
            label: 'Pubs',
            data: top20.map(f => f.properties.pubs_count || 0),
            backgroundColor: '#5fb878',
            borderColor: '#3a8c52',
            borderWidth: 1,
            yAxisID: 'y1',
          },
        ],
      },
      options: {
        indexAxis: 'y',
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: '#e6edf3' }, grid: { color: '#30363d' } },
          y: { ticks: { color: '#e6edf3', font: { size: 10 } }, grid: { color: '#30363d' } },
        },
        plugins: { legend: { labels: { color: '#e6edf3' } } },
      },
    });

    // ---- Chart 3: Evolución temporal (top 12) ----
    const top12 = [...feats]
      .sort((a, b) => (b.properties.pubs_count || 0) - (a.properties.pubs_count || 0))
      .slice(0, 12);
    const decades = ['pre-2010', '2010-2014', '2015-2019', '2020-2026'];
    const decadeColors = ['#8b949e', '#3498db', '#5fb878', '#e74c3c'];
    new Chart(document.getElementById('chart-temporal').getContext('2d'), {
      type: 'bar',
      data: {
        labels: top12.map(f => f.properties.nombre),
        datasets: decades.map((d, i) => ({
          label: d,
          data: top12.map(f => (f.properties.by_decade || {})[d] || 0),
          backgroundColor: decadeColors[i],
          borderWidth: 0,
        })),
      },
      options: {
        maintainAspectRatio: false,
        scales: {
          x: { stacked: true, ticks: { color: '#e6edf3', font: { size: 10 } }, grid: { color: '#30363d' } },
          y: { stacked: true, ticks: { color: '#e6edf3' }, grid: { color: '#30363d' }, beginAtZero: true },
        },
        plugins: { legend: { labels: { color: '#e6edf3' } } },
      },
    });
  } catch (e) {
    console.error('Stats init error:', e);
    document.getElementById('stats-summary').textContent =
      'Error: ' + e.message;
  }
}

// ---------- BedMap ----------
let bedmapMap = null;
let bedmapRaster = null;
let bedmapVectors = { groundingLine: null, coastline: null };
let bedmapCurrentLayer = 'bed';

const BEDMAP_LAYERS = {
  bed: {
    title: 'Elevación del lecho (m)',
    // COG de BedMap3 (Pritchard 2025) reducido a 5 km, servido desde el repo.
    // Range-requests + GeoTIFF rendering en el cliente vía georaster-layer.
    cog: 'data/bedmap3_bed_5km.tif',
    scale: { min: -2700, max: 4500 },
    palette: ['#08306b', '#2171b5', '#6baed6', '#fee391', '#fe9929', '#cc4c02', '#67000d'],
    legend: [
      { color: '#08306b', label: '−2500 m' },
      { color: '#2171b5', label: '−1500 m' },
      { color: '#6baed6', label: '−500 m' },
      { color: '#fee391', label: '0 m' },
      { color: '#fe9929', label: '1500 m' },
      { color: '#cc4c02', label: '3000 m' },
    ],
  },
  surface: {
    title: 'Elevación superficial del hielo (m)',
    cog: 'data/bedmap3_surface_5km.tif',
    scale: { min: 0, max: 4200 },
    palette: ['#f7fbff', '#c6dbef', '#6baed6', '#2171b5', '#08306b'],
    legend: [
      { color: '#f7fbff', label: '0 m' },
      { color: '#c6dbef', label: '500 m' },
      { color: '#6baed6', label: '1500 m' },
      { color: '#2171b5', label: '2500 m' },
      { color: '#08306b', label: '4200 m' },
    ],
  },
  thickness: {
    title: 'Espesor de hielo (m)',
    cog: 'data/bedmap3_thickness_5km.tif',
    scale: { min: 0, max: 5000 },
    palette: ['#fff7fb', '#d0d1e6', '#74a9cf', '#0570b0', '#023858'],
    legend: [
      { color: '#fff7fb', label: '0 m' },
      { color: '#d0d1e6', label: '500 m' },
      { color: '#74a9cf', label: '1500 m' },
      { color: '#0570b0', label: '3000 m' },
      { color: '#023858', label: '5000 m' },
    ],
  },
};

function initBedmap() {
  if (bedmapMap) {
    setTimeout(() => bedmapMap.invalidateSize(), 50);
    return;
  }
  bedmapMap = L.map('bedmap-map', {
    crs: antarcticCRS(),
    center: [-90, 0],
    zoom: 2,
    minZoom: 0,
    maxZoom: 8,
  });
  // Basemap MOA (Mosaic of Antarctica) desde NASA GIBS — polar EPSG:3031
  L.tileLayer.wms('https://gibs.earthdata.nasa.gov/wms/epsg3031/best/wms.cgi', {
    layers: 'MODIS_Terra_Mosaic',
    format: 'image/jpeg',
    transparent: false,
    attribution: 'NASA GIBS · MODIS Mosaic of Antarctica',
  }).addTo(bedmapMap);
  applyBedmapLayer(bedmapCurrentLayer);
  attachBedmapVectors();

  document.querySelectorAll('input[name="bedmap-layer"]').forEach(radio => {
    radio.addEventListener('change', e => {
      if (!e.target.checked) return;
      applyBedmapLayer(e.target.value);
    });
  });
  const glChk = document.getElementById('bedmap-grounding-line');
  const coChk = document.getElementById('bedmap-coastline');
  if (glChk) glChk.addEventListener('change', () => toggleBedmapVector('groundingLine', glChk.checked));
  if (coChk) coChk.addEventListener('change', () => toggleBedmapVector('coastline', coChk.checked));
}

async function applyBedmapLayer(key) {
  bedmapCurrentLayer = key;
  const cfg = BEDMAP_LAYERS[key];
  if (bedmapRaster) bedmapMap.removeLayer(bedmapRaster);
  const status = document.getElementById('bedmap-status');
  if (status) status.textContent = `Cargando ${cfg.title}…`;

  try {
    // Fetch del COG (range-requests soportado por GitHub Pages)
    const response = await fetch(cfg.cog);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const buf = await response.arrayBuffer();
    const georaster = await parseGeoraster(buf);

    // Escala de color: chroma.js para interpolar la palette
    const scale = chroma.scale(cfg.palette).domain([cfg.scale.min, cfg.scale.max]);
    bedmapRaster = new GeoRasterLayer({
      georaster,
      opacity: 0.85,
      resolution: 64,
      pixelValuesToColorFn: vals => {
        const v = vals[0];
        if (v === null || v === undefined || v < -10000) return null;
        return scale(v).hex();
      },
    });
    bedmapRaster.addTo(bedmapMap);
    bedmapMap.fitBounds(bedmapRaster.getBounds(), { padding: [20, 20] });
    if (status) status.innerHTML = `<strong>${cfg.title}</strong><br>BedMap3 (Pritchard 2025, 5km downsample)`;
  } catch (e) {
    console.error('BedMap COG load error:', e);
    if (status) status.innerHTML =
      `⚠ COG no disponible (${e.message}).<br>` +
      'Generar local con:<br><code>python scripts/build_bedmap.py</code><br>' +
      '<code>python scripts/bedmap3_to_cog.py</code>';
  }

  document.getElementById('bedmap-legend-title').textContent = cfg.title;
  const legend = document.getElementById('bedmap-legend-scale');
  clear(legend);
  cfg.legend.forEach(item => {
    const row = el('div', { style: { display: 'flex', alignItems: 'center', gap: '0.5rem', margin: '0.2rem 0' } });
    row.appendChild(el('span', { style: { width: '20px', height: '12px', background: item.color, border: '1px solid #000', display: 'inline-block' } }));
    row.appendChild(el('span', { text: item.label }));
    legend.appendChild(row);
  });
}

async function attachBedmapVectors() {
  // Vectores SCAR ADD v7.7 medium-res (simplificados 5km), bajados con
  // scripts/build_bedmap.py o manualmente desde data.bas.ac.uk/items/...
  const layerConfigs = [
    { key: 'groundingLine', file: 'add_coastline_grounding_line.geojson',
      style: { color: '#f1c40f', weight: 1.4, fillOpacity: 0 },
      checkbox: 'bedmap-grounding-line' },
    { key: 'coastline', file: 'add_coastline_ice_coastline.geojson',
      style: { color: '#e74c3c', weight: 1, fillOpacity: 0 },
      checkbox: 'bedmap-coastline' },
    { key: 'rockCoastline', file: 'add_coastline_rock_coastline.geojson',
      style: { color: '#9c640c', weight: 1.2, fillOpacity: 0 },
      checkbox: 'bedmap-coastline' },  // muestra cuando coastline está on
    { key: 'iceShelf', file: 'add_coastline_ice_shelf_and_front.geojson',
      style: { color: '#3498db', weight: 1, dashArray: '3,2', fillOpacity: 0 },
      checkbox: 'bedmap-coastline' },
  ];
  for (const cfg of layerConfigs) {
    try {
      const data = await fetch('data/' + cfg.file).then(r => r.json());
      bedmapVectors[cfg.key] = L.geoJSON(data, { style: cfg.style });
      if (document.getElementById(cfg.checkbox)?.checked) {
        bedmapVectors[cfg.key].addTo(bedmapMap);
      }
    } catch (e) {
      console.warn(`BedMap vector ${cfg.file} no disponible`, e);
    }
  }
}

function toggleBedmapVector(key, show) {
  // El toggle 'coastline' controla 3 capas (ice/rock/iceShelf)
  const groups = {
    groundingLine: ['groundingLine'],
    coastline: ['coastline', 'rockCoastline', 'iceShelf'],
  };
  (groups[key] || [key]).forEach(k => {
    const layer = bedmapVectors[k];
    if (!layer) return;
    if (show) layer.addTo(bedmapMap); else bedmapMap.removeLayer(layer);
  });
}

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
  if (state.antarticaMode === 'simplecode') {
    if (state.antarticaSimplecode) return;
    try {
      state.antarticaSimplecode = await fetch('data/antartica_simplecode.geojson').then(r => r.json());
    } catch (e) {
      console.warn('No se pudo cargar antartica_simplecode.geojson', e);
      state.antarticaSimplecode = { type: 'FeatureCollection', features: [] };
    }
    return;
  }
  if (state.antartica) return;
  try {
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

let antarticGeositiosLayer = null;
async function ensureAntarticGeositiosLoaded() {
  if (state.antarticGeositios) return;
  try {
    // Mergeamos: catalogados (ASPAs + SCAR) + propuestos (bibliometría SCAR)
    const [cat, prop] = await Promise.all([
      fetch('data/antartica_geositios.geojson').then(r => r.json()).catch(() => ({features: []})),
      fetch('data/antartica_geositios_propuestos.geojson').then(r => r.json()).catch(() => ({features: []})),
    ]);
    state.antarticGeositios = {
      type: 'FeatureCollection',
      features: [...(cat.features || []), ...(prop.features || [])],
    };
    console.log(`[geositios] ${cat.features?.length || 0} catalogados + ${prop.features?.length || 0} propuestos bibliométrica`);
  } catch (e) {
    console.warn('antartica_geositios.geojson no disponible — corre scripts/build_antartica_geositios.py + analisis_actas_scar.py', e);
    state.antarticGeositios = { type: 'FeatureCollection', features: [] };
  }
}

async function renderAntarticGeositiosLayer() {
  if (antarticGeositiosLayer) {
    state.map.removeLayer(antarticGeositiosLayer);
    antarticGeositiosLayer = null;
  }
  if (!state.showAntarticGeositios || state.filterRegion !== 'antartica') return;
  await ensureAntarticGeositiosLoaded();
  antarticGeositiosLayer = L.geoJSON(state.antarticGeositios, {
    pointToLayer: (feature, latlng) => {
      const tipo = (feature.properties.tipo || '').toLowerCase();
      // ASPA en rojo, geositios SCAR en azul, IUGS en dorado
      // ASPA rojo, SCAR azul, IUGS dorado, candidato bibliométrico violeta hueco
      let color = '#5fb878';
      let weight = 1, opacity = 0.92, radius = 6;
      if (tipo.includes('aspa')) color = '#e74c3c';
      else if (tipo.includes('iugs')) color = '#f1c40f';
      else if (tipo.includes('scar')) color = '#3498db';
      else if (tipo.includes('candidato')) {
        color = '#9b59b6'; opacity = 0.6; weight = 2; radius = 7;
      }
      return L.circleMarker(latlng, {
        radius, color: '#000', weight, fillColor: color, fillOpacity: opacity,
      });
    },
    onEachFeature: (feature, layer) => {
      const p = feature.properties;
      layer.bindPopup(
        `<strong>${p.nombre || p.name || 'Sin nombre'}</strong><br>` +
        `<span style="color:#888;font-size:0.8em">${p.codigo || ''} · ${p.tipo || ''}</span><br>` +
        `<em>${p.interes || p.framework || ''}</em><br>` +
        `<small>${p.fuente || ''}</small><br>` +
        (p.descripcion ? `<details><summary>Más info</summary>${p.descripcion}</details>` : '')
      );
    },
  }).addTo(state.map);
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
    // Mergeamos los 49 oficiales SERNAGEOMIN + los candidatos bibliométricos chilenos
    const [oficial, prop] = await Promise.all([
      fetch('data/geositios_inventario_nacional.geojson').then(r => r.json()).catch(() => ({features: []})),
      fetch('data/chile_geositios_propuestos.geojson').then(r => r.json()).catch(() => ({features: []})),
    ]);
    state.geositios = {
      type: 'FeatureCollection',
      features: [...(oficial.features || []), ...(prop.features || [])],
    };
    console.log(`[geositios CL] ${oficial.features?.length || 0} oficiales + ${prop.features?.length || 0} propuestos bibliométrica`);
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
      const tipo = (feature.properties.tipo || '').toLowerCase();
      const escala = (feature.properties['ESCALA DE RELEVANCIA'] || '').toLowerCase();
      let color = '#fff', weight = 1, opacity = 0.95, radius = 7;
      // Candidatos bibliométrica chilena: violeta hueco
      if (tipo.includes('candidato-chile')) {
        color = '#9b59b6'; opacity = 0.55; weight = 2; radius = 6;
      } else if (escala.includes('internacional')) color = '#e74c3c';
      else if (escala.includes('nacional')) color = '#f39c12';
      else if (escala.includes('regional')) color = '#3498db';
      else color = '#95a5a6';
      return L.circleMarker(latlng, { radius, color: '#000', weight, fillColor: color, fillOpacity: opacity });
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
  await renderAntarticGeositiosLayer();
  await renderAntarticHeatmap();

  // Mostrar/ocultar controles propios de Antártica
  const antCtrl = document.getElementById('antartica-controls');
  if (antCtrl) antCtrl.style.display = state.filterRegion === 'antartica' ? '' : 'none';

  let source;
  if (state.filterRegion === 'antartica') {
    await ensureAntarticaLoaded();
    source = state.antarticaMode === 'simplecode'
      ? (state.antarticaSimplecode?.features || [])
      : (state.antartica?.features || []);
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

document.querySelectorAll('input[name="antartica-mode"]').forEach(radio => {
  radio.addEventListener('change', e => {
    if (!e.target.checked) return;
    state.antarticaMode = e.target.value;
    state.filterTypes.clear();
    state.filterAges.clear();
    renderContextos();
  });
});

const toggleAntGeo = document.getElementById('toggle-antartic-geositios');
if (toggleAntGeo) {
  toggleAntGeo.addEventListener('change', e => {
    state.showAntarticGeositios = e.target.checked;
    renderAntarticGeositiosLayer();
  });
}

const toggleAntHeatmap = document.getElementById('toggle-antartic-heatmap');
if (toggleAntHeatmap) {
  toggleAntHeatmap.addEventListener('change', e => {
    state.showAntarticHeatmap = e.target.checked;
    renderAntarticHeatmap();
  });
}

let antarticHeatmapLayer = null;
async function renderAntarticHeatmap() {
  if (antarticHeatmapLayer) {
    state.map.removeLayer(antarticHeatmapLayer);
    antarticHeatmapLayer = null;
  }
  if (!state.showAntarticHeatmap || state.filterRegion !== 'antartica') return;
  await ensureAntarticGeositiosLoaded();
  // Convertir coords WGS84 → EPSG:3031 (proj4) → píxeles del CRS polar
  // pero L.heatLayer espera [lat, lon, intensity] en lat/lon (no proyectados).
  // Para CRS custom, hacemos la conversión a coordenadas planares EPSG:3031
  // y las pasamos como pseudo-lat/lon que el CRS polar entiende.
  const feats = state.antarticGeositios.features || [];
  const points = feats.map(f => {
    const [lon, lat] = f.geometry.coordinates;
    // Intensidad: si tiene pubs_count úsalo (max 50→1.0), si no, base 0.5
    const pubs = f.properties.pubs_count || 5;
    const intensity = Math.min(pubs / 40, 1.0);
    return [lat, lon, intensity];
  });
  antarticHeatmapLayer = L.heatLayer(points, {
    radius: 35, blur: 25, max: 1.0, minOpacity: 0.3,
    gradient: { 0.2: '#3498db', 0.4: '#5fb878', 0.6: '#f1c40f', 0.8: '#e67e22', 1.0: '#e74c3c' },
  });
  antarticHeatmapLayer.addTo(state.map);
}

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
