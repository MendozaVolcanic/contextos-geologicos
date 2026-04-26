# Deploy del dashboard

La app es estática (HTML + JS + GeoJSON), así que la puedes hostear en cualquier CDN. Estas son las dos opciones más rápidas con repo privado.

## Opción A — Cloudflare Pages (recomendada)

1. Crear cuenta gratis en https://dash.cloudflare.com/sign-up (o login si ya tienes).
2. En el dashboard de Cloudflare → **Workers & Pages** → **Create application** → pestaña **Pages** → **Connect to Git**.
3. Autorizar el GitHub App de Cloudflare para acceder al repo `MendozaVolcanic/contextos-geologicos`.
4. Seleccionar el repo y hacer click en **Begin setup**.
5. Configuración:
   - **Project name:** `contextos-geologicos` (o lo que quieras; será el subdominio)
   - **Production branch:** `main`
   - **Framework preset:** None
   - **Build command:** *(dejar vacío)*
   - **Build output directory:** `app`
6. **Save and Deploy**.
7. En ~2 minutos tendrás la URL pública: `https://contextos-geologicos.pages.dev`

Cada `git push` a `main` redespliega automáticamente.

### Dominio personalizado (opcional)
En el proyecto → **Custom domains** → agregar `contextos.tudominio.cl` o similar.

## Opción B — Netlify

1. Sign up en https://app.netlify.com/signup (con GitHub).
2. **Add new site** → **Import an existing project** → GitHub → seleccionar repo.
3. Configuración:
   - **Base directory:** `app`
   - **Build command:** *(vacío)*
   - **Publish directory:** `app`
4. **Deploy site**.
5. URL: `https://random-name-xxx.netlify.app` (renombrable en Site settings).

## Opción C — GitHub Pages (requiere repo público)

Si decides hacer público el repo (`gh repo edit MendozaVolcanic/contextos-geologicos --visibility public --accept-visibility-change-consequences`):

1. En el repo en GitHub → **Settings** → **Pages**.
2. **Source:** Deploy from a branch.
3. **Branch:** `main` / `/app` *(no se puede servir un subdir, hay que mover `app/*` a la raíz o usar GitHub Actions)*.
4. Alternativa más limpia con Actions: usar el workflow `actions/deploy-pages` apuntando a `app/`.

## Notas

- Los archivos `app/data/*.geojson` (~24 MB combinados) están commiteados al repo.
- CesiumJS y Leaflet se sirven vía CDN (unpkg, cloudflare cdnjs, cesium.com), no requieren build local.
- Para Cesium, la app no usa token Ion, así que no necesitas configurar variables de entorno.
