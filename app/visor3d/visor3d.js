/**
 * Visor 3D antártico — relieve BedMap3 + geología GeoMAP + contextos GEOCON.
 *
 * Los datos los prepara scripts/build_visor3d_data.py: tres mallas de elevación
 * como int16 crudo y dos texturas temáticas rasterizadas sobre la misma grilla,
 * así que relieve y temática quedan alineados píxel a píxel.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const ANCHO_MUNDO = 1000;          // el continente ocupa 1000 unidades de escena
const RUTA = 'data/';

// Rampas hipsométricas por capa. Cada una es una lista de [posición 0-1, color].
const RAMPAS = {
  surface: [[0, '#1c3d5a'], [.08, '#3f7fa6'], [.25, '#a8cfe0'],
            [.55, '#dceaf2'], [1, '#ffffff']],
  bed:     [[0, '#08182e'], [.30, '#1b4a72'], [.46, '#3c7ea8'], [.50, '#2e6b3f'],
            [.62, '#7a9a4a'], [.75, '#a8853f'], [.88, '#8a6141'], [1, '#f2f2f2']],
  thickness: [[0, '#0b1b2b'], [.2, '#164b6e'], [.45, '#3b8fb5'],
              [.7, '#93cfe3'], [1, '#f0fbff']],
};

// [clave, color, radio]. El orden es el de la jerarquía SCAR, de aprobado a
// simple área protegida — que no es un geositio en absoluto.
const ESTATUS = [
  ['aprobado',  0xffd24a, 4.6],
  ['nominado',  0xff9d4a, 3.8],
  ['potencial', 0x5fd0a0, 2.8],
  ['aspa',      0x8fa8c0, 2.4],
];

const ETIQUETA_ESTATUS = {
  aprobado: 'Geositio SCAR aprobado',
  nominado: 'Nominado (GF3/GF4, sin resolver)',
  potencial: 'Potencial — derivado de bibliografía, sin estatus SCAR',
  aspa: 'ASPA · área protegida del Tratado, no es un geositio',
};

const NOTAS = {
  surface: 'Altura de la superficie del hielo. Solo hay dato donde hay hielo o roca; el océano queda como hueco.',
  bed: 'Topografía del lecho bajo el hielo, incluida la batimetría. Es la capa con mayor cobertura.',
  thickness: 'Espesor del hielo. No es una elevación: el relieve representa cuánto hielo hay encima.',
};

let escena, camara, render, controles, malla, grupoPuntos;
let meta, elevaciones = {}, capaActiva = 'surface', temaActivo = 'ninguno';
let exageracion = 60, opacidadTema = .85;
let escalaZ, texturas = {};
const rayo = new THREE.Raycaster();
const puntero = new THREE.Vector2();

/* ------------------------------------------------------------------ */
/* Carga                                                               */
/* ------------------------------------------------------------------ */

async function cargar() {
  meta = await (await fetch(RUTA + 'meta.json')).json();

  const nombres = Object.keys(meta.capas);
  const buffers = await Promise.all(
    nombres.map(n => fetch(RUTA + meta.capas[n].archivo).then(r => r.arrayBuffer())));
  nombres.forEach((n, i) => { elevaciones[n] = new Int16Array(buffers[i]); });

  const cargador = new THREE.TextureLoader();
  for (const [clave, archivo] of [['geologia', 'geologia.png'], ['geocon', 'geocon.png']]) {
    texturas[clave] = await cargador.loadAsync(RUTA + archivo);
    texturas[clave].colorSpace = THREE.SRGBColorSpace;
    texturas[clave].magFilter = THREE.NearestFilter;   // clases discretas: sin interpolar
    texturas[clave].minFilter = THREE.LinearMipmapLinearFilter;
  }

  const [izq, , der] = meta.bounds;
  escalaZ = ANCHO_MUNDO / (der - izq);                 // metros → unidades de escena
}

/* ------------------------------------------------------------------ */
/* Rampa de color como textura 1D                                      */
/* ------------------------------------------------------------------ */

function texturaRampa(paradas) {
  const c = document.createElement('canvas');
  c.width = 256; c.height = 1;
  const g = c.getContext('2d').createLinearGradient(0, 0, 256, 0);
  paradas.forEach(([p, col]) => g.addColorStop(p, col));
  const ctx = c.getContext('2d');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 256, 1);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  return t;
}

function cssRampa(paradas) {
  return `linear-gradient(90deg, ${paradas.map(([p, c]) => `${c} ${p * 100}%`).join(', ')})`;
}

/* ------------------------------------------------------------------ */
/* Geometría del terreno                                               */
/* ------------------------------------------------------------------ */

function construirGeometria() {
  const n = meta.malla;
  const nodata = meta.capas[capaActiva].nodata;
  const datos = elevaciones[capaActiva];

  const pos = new Float32Array(n * n * 3);
  const uv = new Float32Array(n * n * 2);
  const elev = new Float32Array(n * n);
  const valido = new Uint8Array(n * n);

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const k = i * n + j;
      const v = datos[k];
      const ok = v !== nodata;
      valido[k] = ok ? 1 : 0;
      const h = ok ? v : 0;
      elev[k] = h;
      pos[k * 3]     = (j / (n - 1) - .5) * ANCHO_MUNDO;
      pos[k * 3 + 1] = h * escalaZ * exageracion;
      pos[k * 3 + 2] = (i / (n - 1) - .5) * ANCHO_MUNDO;
      // fila 0 del ráster es el norte (y máximo); v=1 arriba para que la textura calce
      uv[k * 2]     = j / (n - 1);
      uv[k * 2 + 1] = 1 - i / (n - 1);
    }
  }

  // Índices: se omite el cuadrilátero si alguna de sus cuatro esquinas es nodata,
  // así el océano queda como hueco real en vez de una lámina plana a cota cero.
  const idx = [];
  for (let i = 0; i < n - 1; i++) {
    for (let j = 0; j < n - 1; j++) {
      const a = i * n + j, b = a + 1, c = a + n, d = c + 1;
      if (!(valido[a] && valido[b] && valido[c] && valido[d])) continue;
      idx.push(a, c, b, b, c, d);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  geo.setAttribute('elev', new THREE.BufferAttribute(elev, 1));
  geo.setIndex(idx);
  geo.computeVertexNormals();
  return geo;
}

function material() {
  const { min, max } = meta.capas[capaActiva];
  return new THREE.ShaderMaterial({
    uniforms: {
      uRampa: { value: texturaRampa(RAMPAS[capaActiva]) },
      uTema: { value: texturas.geologia },
      uTemaOn: { value: 0 },
      uOpacidad: { value: opacidadTema },
      uMin: { value: min },
      uMax: { value: max },
      uLuz: { value: new THREE.Vector3(0.45, 0.8, 0.35).normalize() },
    },
    vertexShader: `
      attribute float elev;
      uniform float uMin, uMax;
      varying float vT;
      varying vec2 vUv;
      varying vec3 vNormal;
      void main() {
        vT = clamp((elev - uMin) / max(uMax - uMin, 1.0), 0.0, 1.0);
        vUv = uv;
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }`,
    fragmentShader: `
      uniform sampler2D uRampa, uTema;
      uniform float uTemaOn, uOpacidad;
      uniform vec3 uLuz;
      varying float vT;
      varying vec2 vUv;
      varying vec3 vNormal;
      void main() {
        vec3 base = texture2D(uRampa, vec2(vT, 0.5)).rgb;
        vec4 tema = texture2D(uTema, vUv);
        vec3 col = mix(base, tema.rgb, tema.a * uOpacidad * uTemaOn);
        vec3 nrm = normalize(vNormal);
        float lam = abs(dot(nrm, normalize(uLuz)));
        gl_FragColor = vec4(col * (0.42 + 0.72 * lam), 1.0);
      }`,
    side: THREE.DoubleSide,
  });
}

function rehacerTerreno() {
  if (malla) {
    malla.geometry.dispose();
    malla.material.uniforms.uRampa.value.dispose();
    malla.material.dispose();
    escena.remove(malla);
  }
  malla = new THREE.Mesh(construirGeometria(), material());
  escena.add(malla);
  aplicarTema();
  document.getElementById('nota-capa').textContent = NOTAS[capaActiva];
  dibujarLeyenda();
  colocarPuntos();
}

function actualizarExageracion() {
  const n = meta.malla;
  const pos = malla.geometry.attributes.position;
  const elev = malla.geometry.attributes.elev;
  for (let k = 0; k < n * n; k++) {
    pos.array[k * 3 + 1] = elev.array[k] * escalaZ * exageracion;
  }
  pos.needsUpdate = true;
  malla.geometry.computeVertexNormals();
  colocarPuntos();
}

/* ------------------------------------------------------------------ */
/* Coordenadas: grilla ↔ EPSG:3031 ↔ lat/lon                           */
/* ------------------------------------------------------------------ */

function alturaEn(x3031, y3031) {
  const [izq, aba, der, arr] = meta.bounds;
  const n = meta.malla;
  const j = Math.round((x3031 - izq) / (der - izq) * (n - 1));
  const i = Math.round((arr - y3031) / (arr - aba) * (n - 1));
  if (i < 0 || j < 0 || i >= n || j >= n) return null;
  const v = elevaciones[capaActiva][i * n + j];
  return v === meta.capas[capaActiva].nodata ? null : v;
}

function mundoDesde3031(x3031, y3031) {
  const [izq, aba, der, arr] = meta.bounds;
  return {
    x: ((x3031 - izq) / (der - izq) - .5) * ANCHO_MUNDO,
    z: ((arr - y3031) / (arr - aba) - .5) * ANCHO_MUNDO,
  };
}

/** Inversa de la estereográfica polar antártica (EPSG:3031) — Snyder, WGS84. */
function aLatLon(x, y) {
  const a = 6378137.0, e = 0.081819190842621, phiC = -71 * Math.PI / 180;
  // Se trabaja en el aspecto norte y se invierte el signo al final.
  const px = -x, py = -y, pc = -phiC;
  const sc = Math.sin(pc);
  const tC = Math.tan(Math.PI / 4 - pc / 2) / Math.pow((1 - e * sc) / (1 + e * sc), e / 2);
  const mC = Math.cos(pc) / Math.sqrt(1 - e * e * sc * sc);
  const rho = Math.hypot(px, py);
  if (rho < 1e-9) return { lat: -90, lon: 0 };
  const t = rho * tC / (a * mC);
  const chi = Math.PI / 2 - 2 * Math.atan(t);
  const e2 = e * e, e4 = e2 * e2, e6 = e4 * e2;
  const phi = chi
    + (e2 / 2 + 5 * e4 / 24 + e6 / 12) * Math.sin(2 * chi)
    + (7 * e4 / 48 + 29 * e6 / 240) * Math.sin(4 * chi)
    + (7 * e6 / 120) * Math.sin(6 * chi);
  const lam = Math.atan2(px, -py);
  return { lat: -phi * 180 / Math.PI, lon: -lam * 180 / Math.PI };
}

/* ------------------------------------------------------------------ */
/* Geositios                                                           */
/* ------------------------------------------------------------------ */

function colocarPuntos() {
  if (grupoPuntos) {
    grupoPuntos.traverse(o => { if (o.geometry) o.geometry.dispose(); });
    escena.remove(grupoPuntos);
  }
  grupoPuntos = new THREE.Group();
  escena.add(grupoPuntos);

  // Los aprobados se dibujan más grandes: son 8 contra 72 ASPAs, y sin eso
  // desaparecen entre el resto.
  for (const [clave, color, radio] of ESTATUS) {
    if (!document.getElementById(`ver-${clave}`).checked) continue;
    const geo = new THREE.SphereGeometry(radio, 12, 10);
    const mat = new THREE.MeshBasicMaterial({ color });
    for (const p of meta[clave] || []) {
      const h = alturaEn(p.x, p.y);
      const w = mundoDesde3031(p.x, p.y);
      const esfera = new THREE.Mesh(geo, mat);
      esfera.position.set(w.x, (h ?? 0) * escalaZ * exageracion + radio + 2, w.z);
      esfera.userData = { punto: p, estatus: clave, altura: h };
      grupoPuntos.add(esfera);
    }
  }
}

function mostrarFicha(datos) {
  const { punto: p, estatus, altura } = datos;
  const nombre = p.nombre || p.name || 'Sin nombre';
  const ll = aLatLon(p.x, p.y);
  const filas = [
    ['Estatus', ETIQUETA_ESTATUS[estatus] || estatus],
    ['Framework', p.framework || '—'],
    ['Posición', `${Math.abs(ll.lat).toFixed(3)}° S · ${ll.lon.toFixed(3)}°`],
    [capaActiva === 'thickness' ? 'Espesor' : 'Elevación',
     altura === null ? 'sin dato' : `${altura.toLocaleString('es')} m`],
  ];
  if (p.fuente) filas.push(['Fuente', p.fuente]);
  if (p.pubs) filas.push(['Publicaciones', p.pubs]);

  const color = (ESTATUS.find(e => e[0] === estatus) || [, 0x888888])[1];
  const insignias =
    (p.iugs_third_100 ? '<span class="insignia iugs">IUGS Third 100</span>' : '') +
    (p.en_espera ? '<span class="insignia espera">no se considera por ahora</span>' : '');

  document.getElementById('ficha-cuerpo').innerHTML =
    `<h3><span class="punto" style="background:#${color.toString(16).padStart(6, '0')}"></span>` +
    `${escapar(nombre)}</h3>${insignias}<dl>` +
    filas.map(([k, v]) => `<dt>${k}</dt><dd>${escapar(String(v))}</dd>`).join('') +
    `</dl>` + (p.descripcion ? `<p class="desc">${escapar(p.descripcion)}</p>` : '');
  document.getElementById('ficha').hidden = false;
}

const escapar = s => String(s).replace(/[&<>"']/g,
  c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/* ------------------------------------------------------------------ */
/* Leyenda                                                             */
/* ------------------------------------------------------------------ */

function dibujarLeyenda() {
  const caja = document.getElementById('leyenda');
  const grupo = document.getElementById('grupo-leyenda');
  grupo.hidden = false;

  if (temaActivo === 'ninguno') {
    const { min, max } = meta.capas[capaActiva];
    caja.innerHTML =
      `<div class="rampa" style="background:${cssRampa(RAMPAS[capaActiva])}"></div>
       <div class="rampa-etiquetas"><span>${min.toLocaleString('es')} m</span>
       <span>${max.toLocaleString('es')} m</span></div>`;
    return;
  }
  const entradas = meta[temaActivo] || [];
  caja.innerHTML = entradas.filter(e => e.pixeles > 0).map(e =>
    `<div class="item-leyenda">
       <div class="muestra" style="background:${e.color}"></div>
       <span>${escapar(e.etiqueta)}</span>
     </div>`).join('');
}

function aplicarTema() {
  const u = malla.material.uniforms;
  u.uTemaOn.value = temaActivo === 'ninguno' ? 0 : 1;
  if (temaActivo !== 'ninguno') u.uTema.value = texturas[temaActivo];
  u.uOpacidad.value = opacidadTema;
  document.getElementById('nota-tema').hidden =
    temaActivo === 'ninguno' || !meta.dilatacion;
  dibujarLeyenda();
}

/* ------------------------------------------------------------------ */
/* Escena                                                              */
/* ------------------------------------------------------------------ */

function iniciar() {
  escena = new THREE.Scene();
  escena.background = new THREE.Color(0x0b1016);
  escena.fog = new THREE.Fog(0x0b1016, 1400, 3000);

  // Math.max(1, …) porque si la página arranca oculta o con el panel colapsado,
  // innerWidth/innerHeight valen 0 y el aspecto de la cámara queda en NaN.
  const ancho = Math.max(1, innerWidth), alto = Math.max(1, innerHeight);
  camara = new THREE.PerspectiveCamera(45, ancho / alto, 1, 6000);
  render = new THREE.WebGLRenderer({ antialias: true });
  render.setSize(ancho, alto);
  render.setPixelRatio(Math.min(devicePixelRatio, 2));
  document.getElementById('lienzo').appendChild(render.domElement);

  controles = new OrbitControls(camara, render.domElement);
  controles.enableDamping = true;
  controles.dampingFactor = .08;
  controles.maxPolarAngle = Math.PI * .92;
  controles.minDistance = 60;
  controles.maxDistance = 2800;

  rehacerTerreno();
  reencuadrar();
  conectarUI();

  addEventListener('resize', () => {
    const w = Math.max(1, innerWidth), h = Math.max(1, innerHeight);
    camara.aspect = w / h;
    camara.updateProjectionMatrix();
    render.setSize(w, h);
    render.render(escena, camara);
  });

  // Handle de depuración: permite forzar un frame o inspeccionar la escena desde
  // la consola. requestAnimationFrame no dispara si la pestaña está oculta, así
  // que sin esto no hay forma de comprobar que el terreno se dibuja.
  window.visor3d = { escena, camara, render, controles,
                     dibujar: () => render.render(escena, camara) };

  render.render(escena, camara);   // primer frame sin esperar a rAF

  (function animar() {
    requestAnimationFrame(animar);
    controles.update();
    render.render(escena, camara);
  })();
}

function reencuadrar() {
  camara.position.set(0, 620, 900);
  controles.target.set(0, 0, 0);
  controles.update();
}

/* ------------------------------------------------------------------ */
/* Interfaz                                                            */
/* ------------------------------------------------------------------ */

function conectarUI() {
  document.querySelectorAll('#sel-capa button').forEach(b => {
    b.onclick = () => {
      document.querySelectorAll('#sel-capa button').forEach(x => x.classList.remove('activo'));
      b.classList.add('activo');
      capaActiva = b.dataset.capa;
      rehacerTerreno();
    };
  });

  document.querySelectorAll('#sel-tema button').forEach(b => {
    b.onclick = () => {
      document.querySelectorAll('#sel-tema button').forEach(x => x.classList.remove('activo'));
      b.classList.add('activo');
      temaActivo = b.dataset.tema;
      aplicarTema();
    };
  });

  const exag = document.getElementById('exag');
  exag.oninput = () => {
    exageracion = +exag.value;
    document.getElementById('val-exag').textContent = `${exageracion}×`;
    actualizarExageracion();
  };

  const op = document.getElementById('opacidad');
  op.oninput = () => {
    opacidadTema = op.value / 100;
    document.getElementById('val-opacidad').textContent = `${op.value}%`;
    malla.material.uniforms.uOpacidad.value = opacidadTema;
  };

  for (const [clave] of ESTATUS) {
    document.getElementById(`ver-${clave}`).onchange = colocarPuntos;
    document.getElementById(`n-${clave}`).textContent = (meta[clave] || []).length;
  }
  document.getElementById('reset').onclick = reencuadrar;
  document.getElementById('cerrar-ficha').onclick =
    () => { document.getElementById('ficha').hidden = true; };

  render.domElement.addEventListener('pointermove', sondear);
  render.domElement.addEventListener('click', clic);
}

function coordsPuntero(ev) {
  puntero.x = (ev.clientX / innerWidth) * 2 - 1;
  puntero.y = -(ev.clientY / innerHeight) * 2 + 1;
  rayo.setFromCamera(puntero, camara);
}

function sondear(ev) {
  coordsPuntero(ev);
  const caja = document.getElementById('sonda');
  const hit = rayo.intersectObject(malla)[0];
  if (!hit) { caja.hidden = true; return; }

  const metros = hit.point.y / (escalaZ * exageracion);
  const [izq, aba, der, arr] = meta.bounds;
  const x3031 = izq + (hit.point.x / ANCHO_MUNDO + .5) * (der - izq);
  const y3031 = arr - (hit.point.z / ANCHO_MUNDO + .5) * (arr - aba);
  const ll = aLatLon(x3031, y3031);
  const etiqueta = capaActiva === 'thickness' ? 'espesor' : 'elev';

  caja.innerHTML = `${ll.lat.toFixed(2)}° S · ${ll.lon.toFixed(2)}°  ·  ` +
                   `${etiqueta} ${Math.round(metros).toLocaleString('es')} m`;
  caja.style.left = `${ev.clientX + 14}px`;
  caja.style.top = `${ev.clientY + 14}px`;
  caja.hidden = false;
}

function clic(ev) {
  coordsPuntero(ev);
  const hit = rayo.intersectObjects(grupoPuntos.children)[0];
  if (hit) mostrarFicha(hit.object.userData);
}

/* ------------------------------------------------------------------ */

cargar().then(() => {
  iniciar();
  const c = document.getElementById('cargando');
  c.classList.add('oculto');
  setTimeout(() => { c.style.display = 'none'; }, 450);
}).catch(err => {
  document.getElementById('cargando').innerHTML =
    `<p style="color:#e08a8a">No se pudieron cargar los datos.<br>${escapar(err.message)}</p>
     <p>¿Corriste <code>python scripts/build_visor3d_data.py</code>?</p>`;
  console.error(err);
});
