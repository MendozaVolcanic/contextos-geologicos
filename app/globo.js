// Vista 3D con CesiumJS — sin token Ion (usa Natural Earth II que viene con Cesium).
// Carga lazy: solo se inicializa cuando el usuario entra a la pestaña Globo 3D.

const globoState = {
  viewer: null,
  layers: { chile: null, antartica: null, cgt: null },
  initialized: false,
  initializing: false,
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
    duration: 1.5,
  });
}

async function loadGeoJsonAs(viewer, url, defaultColor) {
  // clampToGround: false → mucho más rápido (no calcula intersección con terreno)
  // stroke=undefined, fill aplicado por entidad desde properties.color
  const ds = await Cesium.GeoJsonDataSource.load(url, {
    clampToGround: false,
    stroke: Cesium.Color.WHITE.withAlpha(0.0),
    strokeWidth: 0,
    fill: defaultColor,
  });
  for (const entity of ds.entities.values) {
    const props = entity.properties;
    const colorHex = props && props.color && props.color.getValue();
    if (entity.polygon && colorHex) {
      const c = Cesium.Color.fromCssColorString(colorHex).withAlpha(0.7);
      entity.polygon.material = c;
      entity.polygon.outline = false;
      // Pequeña altura sobre el suelo para evitar z-fighting con la imagery
      entity.polygon.height = 0;
    }
  }
  await viewer.dataSources.add(ds);
  return ds;
}

function setStatus(msg) {
  const el = document.getElementById('globo-status');
  if (el) el.textContent = msg || '';
}

async function initGlobo() {
  if (globoState.initialized || globoState.initializing) return;
  globoState.initializing = true;

  try {
    Cesium.Ion.defaultAccessToken = '';
    setStatus('Inicializando globo…');

    // baseLayer: false → no intentar Ion. Después agrego Natural Earth II como imagery.
    const viewer = new Cesium.Viewer('cesium-container', {
      baseLayer: false,
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
      requestRenderMode: true,
    });

    viewer.scene.globe.enableLighting = false;
    viewer.scene.skyAtmosphere.show = true;
    viewer.scene.backgroundColor = Cesium.Color.fromCssColorString('#000814');
    globoState.viewer = viewer;

    // Imagery: Natural Earth II que viene con Cesium (no requiere token, no tiene CORS issues)
    setStatus('Cargando imagery…');
    try {
      const provider = await Cesium.TileMapServiceImageryProvider.fromUrl(
        Cesium.buildModuleUrl('Assets/Textures/NaturalEarthII')
      );
      viewer.imageryLayers.addImageryProvider(provider);
    } catch (e) {
      console.warn('Natural Earth II falló, probando provider alternativo', e);
      // Fallback: ArcGIS World Imagery (CORS friendly)
      try {
        const fallback = await Cesium.ArcGisMapServerImageryProvider.fromUrl(
          'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer'
        );
        viewer.imageryLayers.addImageryProvider(fallback);
      } catch (e2) {
        console.error('Sin imagery base disponible', e2);
      }
    }

    // Cargar capas en paralelo (NO bloquea el render del globo)
    setStatus('Cargando capas geológicas…');
    const tasks = [
      loadGeoJsonAs(viewer, 'data/chile_geologico.geojson').then(ds => globoState.layers.chile = ds),
      loadGeoJsonAs(viewer, 'data/antartica_simplecode.geojson').then(ds => globoState.layers.antartica = ds),
      loadGeoJsonAs(viewer, 'data/contextos.geojson').then(ds => globoState.layers.cgt = ds),
    ];
    await Promise.allSettled(tasks);
    setStatus('');

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

    globoState.initialized = true;
  } catch (e) {
    console.error('Error inicializando globo:', e);
    setStatus('Error: ' + e.message);
  } finally {
    globoState.initializing = false;
  }
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
