// Vista 3D con CesiumJS — sin token Ion (usa imagery OSM gratuito).
// Carga lazy: solo se inicializa cuando el usuario entra a la pestaña Globo 3D.

const globoState = {
  viewer: null,
  layers: { chile: null, antartica: null, cgt: null },
  initialized: false,
};

const VIEWS = {
  chile: { lon: -71, lat: -38, height: 4_000_000 },
  antartica: { lon: 0, lat: -90, height: 12_000_000 },
  continente: { lon: -65, lat: -55, height: 14_000_000 },
  globo: { lon: -70, lat: -30, height: 25_000_000 },
};

function flyTo(view) {
  if (!globoState.viewer) return;
  const v = VIEWS[view];
  globoState.viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(v.lon, v.lat, v.height),
    orientation: { heading: 0, pitch: -Cesium.Math.PI_OVER_TWO, roll: 0 },
    duration: 1.5,
  });
}

async function loadGeoJsonAs(viewer, url, opts = {}) {
  const ds = await Cesium.GeoJsonDataSource.load(url, {
    clampToGround: true,
    ...opts,
  });
  // Pintar cada entidad con su propio color desde properties.color
  for (const entity of ds.entities.values) {
    const props = entity.properties;
    const colorHex = props && props.color && props.color.getValue();
    if (entity.polygon && colorHex) {
      const c = Cesium.Color.fromCssColorString(colorHex);
      entity.polygon.material = c.withAlpha(0.55);
      entity.polygon.outline = false;
    }
  }
  await viewer.dataSources.add(ds);
  return ds;
}

async function initGlobo() {
  if (globoState.initialized) return;
  globoState.initialized = true;

  // Sin token: usar OSM imagery (no requiere Ion)
  Cesium.Ion.defaultAccessToken = '';

  const viewer = new Cesium.Viewer('cesium-container', {
    baseLayerPicker: false,
    geocoder: false,
    homeButton: false,
    sceneModePicker: false,
    navigationHelpButton: false,
    timeline: false,
    animation: false,
    fullscreenButton: false,
    infoBox: false,
    selectionIndicator: false,
    imageryProvider: new Cesium.OpenStreetMapImageryProvider({
      url: 'https://tile.openstreetmap.org/',
    }),
  });

  viewer.scene.globe.enableLighting = false;
  viewer.scene.skyAtmosphere.show = true;
  viewer.scene.backgroundColor = Cesium.Color.fromCssColorString('#000814');

  globoState.viewer = viewer;

  // Cargar capas en paralelo
  try {
    const [chileDs, antDs, cgtDs] = await Promise.all([
      loadGeoJsonAs(viewer, 'data/chile_geologico.geojson'),
      loadGeoJsonAs(viewer, 'data/antartica_simplecode.geojson'),
      loadGeoJsonAs(viewer, 'data/contextos.geojson'),
    ]);
    globoState.layers.chile = chileDs;
    globoState.layers.antartica = antDs;
    globoState.layers.cgt = cgtDs;
  } catch (e) {
    console.error('Error cargando capas en globo:', e);
  }

  // Vista inicial
  flyTo('continente');

  // Click handler
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
  handler.setInputAction((click) => {
    const picked = viewer.scene.pick(click.position);
    if (Cesium.defined(picked) && picked.id && picked.id.properties) {
      const p = picked.id.properties;
      showGloboDetail({
        nombre: (p.nombre && p.nombre.getValue()) || (p.geo && p.geo.getValue()) || '—',
        edad: (p.edad && p.edad.getValue()) || (p.epoca && p.epoca.getValue()) || '',
        descripcion: (p.descripcion && p.descripcion.getValue()) || (p.composicio && p.composicio.getValue()) || '',
        clase: (p.clase && p.clase.getValue()) || (p.era && p.era.getValue()) || '',
      });
    } else {
      hideGloboDetail();
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

  // Wire toggles
  document.getElementById('globo-chile').addEventListener('change', e => {
    if (globoState.layers.chile) globoState.layers.chile.show = e.target.checked;
  });
  document.getElementById('globo-antartica').addEventListener('change', e => {
    if (globoState.layers.antartica) globoState.layers.antartica.show = e.target.checked;
  });
  document.getElementById('globo-cgt').addEventListener('change', e => {
    if (globoState.layers.cgt) globoState.layers.cgt.show = e.target.checked;
  });

  document.querySelectorAll('.btn-view').forEach(btn => {
    btn.addEventListener('click', () => flyTo(btn.dataset.view));
  });

  document.querySelector('#globo-detail .close').addEventListener('click', hideGloboDetail);
}

function showGloboDetail({ nombre, edad, descripcion, clase }) {
  const panel = document.getElementById('globo-detail');
  panel.classList.remove('hidden');
  document.getElementById('tab-globo').classList.add('with-detail');
  document.getElementById('globo-detail-name').textContent = nombre;
  document.getElementById('globo-detail-meta').textContent = [clase, edad].filter(Boolean).join(' · ');
  document.getElementById('globo-detail-desc').textContent = descripcion || '—';
}

function hideGloboDetail() {
  document.getElementById('globo-detail').classList.add('hidden');
  document.getElementById('tab-globo').classList.remove('with-detail');
}

window.initGlobo = initGlobo;
