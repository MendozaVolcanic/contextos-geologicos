# Estado del proyecto — Suite Geopatrimonio

**Última actualización:** 2026-08-25

Documento de estado del traspaso. `README.md` explica **qué hace** el proyecto y
`TRASPASO.md` **qué falta por hacer**; este archivo dice **dónde está cada cosa hoy** y
cómo quedó el reparto de responsabilidades.

---

## 1. Quién mantiene esto

El proyecto pasó a continuidad de **Felipe Fuentes Carrasco**
([`felipefuentescarrasco-web`](https://github.com/felipefuentescarrasco-web)) el
**2026-08-24**, con permiso `write` aceptado y activo en los cinco repos de la Suite.
Nicolás Mendoza queda como autor original y propietario de los repos.

## 2. Dónde vive el proyecto

⚠️ **Ya no existe copia local en el computador de Nicolás.** Las carpetas
`Diversion\Contextos geologicos`, `Diversion\Glaciar Antartico` y
`Diversion\Suite-Geopatrimonio` se eliminaron el 2026-08-24 tras verificar, archivo por
archivo, que todo estuviera respaldado. GitHub es ahora la copia primaria.

| Qué | Dónde | Tamaño |
|---|---|---|
| Código, dashboards y GeoJSON derivados | Los 5 repos de GitHub | ~75 MB |
| Datos pesados de terceros | 5 ZIP en Google Drive (`traspaso-geopatrimonio`) | 2,95 GB |
| Instrucciones de restauración | `LEEME_PRIMERO.md` y `restaurar.py`, junto a los ZIP | — |

Los cinco repos, todos públicos y con GitHub Pages:

| Repo | Rol |
|---|---|
| [contextos-geologicos](https://github.com/MendozaVolcanic/contextos-geologicos) | **Maestro.** 22 contextos chilenos + 9 frameworks SCAR, mapa, globo, léxico |
| [glaciar-antartico](https://github.com/MendozaVolcanic/glaciar-antartico) | Velocidades ITS_LIVE, aceleración 2010→2022, predicción IPCC |
| [dashboard-22-contextos](https://github.com/MendozaVolcanic/dashboard-22-contextos) | Gestión de los 22 contextos |
| [apadrina-geositio-chile](https://github.com/MendozaVolcanic/apadrina-geositio-chile) | Ciencia ciudadana sobre los 49 geositios SERNAGEOMIN |
| [georrutas-chile](https://github.com/MendozaVolcanic/georrutas-chile) | Rutas geoturísticas documentadas |

**Para reconstruir el entorno completo:** clonar, y luego extraer los ZIP sobre el clon con
`python restaurar.py "<ruta al repo>"`. El script deja cada cosa en su lugar y verifica el
resultado.

## 3. Qué no está en GitHub, y por qué

3,6 GB de PDFs de terceros (`docs/biblioteca/`) y datasets geoespaciales oficiales
(`docs/mapas/`) están gitignored a propósito: son material con copyright de terceros, seis
archivos superan el límite de 100 MB por archivo de GitHub, y Git es mal contenedor para
binarios grandes. Su procedencia está documentada en
[`docs/bibliografia/PENDIENTES_DESCARGA.md`](docs/bibliografia/PENDIENTES_DESCARGA.md) y el
catálogo bibliográfico completo —131 registros indexados por tema, región y año— **sí está
versionado** en `docs/biblioteca/_db/`.

⚠️ **Excepción a vigilar:** `docs/pdfs/lexico1.txt` y `lexico2.txt` están gitignored como
"regenerables", pero **no existe script que los regenere**: los regex de `build_lexico.py`
dependen del layout exacto del extractor que se usó, y ese dato no quedó registrado. Su
única copia está en `05_lexico_txt.zip` y en Drive. Si algún día se pierden, hay que
re-extraerlos de los PDF (que sí están versionados) y reajustar el parser.

## 4. Qué se corrigió antes de entregar (2026-08-24)

Una auditoría con seis revisores encontró 24 hallazgos. El informe completo está en
[`reviews/code-review/`](reviews/code-review/). Se corrigieron los cuatro críticos:

| Hallazgo | Estado |
|---|---|
| Subdivisiones TAM etiquetadas **F2** cuando el propio repo define Beacon/Ferrar como **F3** | ✅ Corregido y verificado en producción |
| Ocho scripts abortaban con `UnicodeEncodeError` al redirigir la salida a un archivo | ✅ Corregido (UTF-8 forzado en stdout/stderr) |
| El corpus de actas SCAR pesaba **cero** en su propio ranking bibliométrico | ✅ Corregido |
| Sin `requirements.txt`, con 13 dependencias externas sin declarar | ✅ Agregado |

Fuera de esa auditoría, también se corrigieron tres bugs que estaban **publicados**:

- Los tres GeoJSON centrales del visor no eran UTF-8, así que 9 de los 15 nombres de
  contexto se mostraban con caracteres de reemplazo en el sitio público.
- En `dashboard-22-contextos`, los 22 nombres de contexto eran expansiones adivinadas de las
  siglas. Corregidos contra `docs/notas/contextos_chilenos_22_mourgues.md`.
- El hash SRI de Leaflet era inválido en dos dashboards, así que el navegador bloqueaba la
  librería y el mapa no cargaba.

Los 11 hallazgos P2 y 9 P3 restantes están abiertos y documentados en la sección 7 de
[`TRASPASO.md`](TRASPASO.md), separando los que necesitan criterio geológico de los que son
arreglo mecánico.

## 5. Lo que sigue abierto y es decisión de quien continúe

1. **Refrendo de la lista de 22 contextos.** Benado et al. 2019 la describe como cuestionada
   por no haber sido validada por la comunidad geológica nacional. Todo lo demás cuelga de esto.
2. **Reglas de mapping** en `assign_contexto()` — hoy asignan 15 de los 22 contextos, con
   heurísticas de era + período + composición + latitud auditadas en
   `docs/notas/mapping_rules_log.md`.
3. **Mourgues et al. 2012 original** sigue sin conseguirse (SSL caducado del catálogo
   SERNAGEOMIN). Es la fuente primaria para validar todo lo anterior.
4. **En glaciar-antartico**, el producto de aceleración está marcado como preliminar: restar
   dos mosaicos anuales de ITS_LIVE no es un método validado, y el delta arrastra un sesgo
   entre sensores sin corregir. Ver su `TRASPASO.md` §3.

## 6. Mapa de la documentación

| Archivo | Qué contiene |
|---|---|
| `README.md` | Qué hace el proyecto, cómo está construido, cómo reproducirlo |
| `TRASPASO.md` | Qué falta, qué está abierto, qué requiere criterio geológico |
| `ESTADO.md` *(este)* | Dónde está cada cosa hoy y quién mantiene qué |
| `DEPLOY.md` | Cómo desplegar el dashboard |
| `reviews/code-review/` | Auditoría de código completa |
| `docs/notas/` | Razonamiento geológico y listas oficiales |
| `docs/bibliografia/PENDIENTES_DESCARGA.md` | Procedencia de cada dataset y qué falta bajar |
