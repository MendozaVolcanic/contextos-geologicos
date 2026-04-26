# Ideas de geopatrimonio y geoturismo para Chile

Documento maestro derivado de la bibliografía consolidada del proyecto Contextos Geológicos Chilenos (visor GitHub MendozaVolcanic) y del Inventario Nacional de Geositios SERNAGEOMIN 2024 (49 sitios oficiales). Pensado para SGCh / SERNAGEOMIN, operadores turísticos rurales, profesores, comunidades locales y municipios.

---

## 1. Diagnóstico actual

**Lo que Chile tiene.** Existe una arquitectura conceptual sólida: 22 Contextos Geológicos Chilenos preliminares (Mourgues, Schilling y Castro 2012; capítulo Chile del libro UNAM 2016) que cubren desde el Magmatismo Paleozoico (MgPz) hasta los meteoritos (As). Sobre esta arquitectura se montó el Programa de Geositios SGCh (iniciado 2007), que pasó de 63 geositios reconocidos en junio 2016 (Benado et al. 2018) a 66 en 2015 (Martínez et al. 2015) y al inventario oficial SERNAGEOMIN 2024 con 49 geositios validados. La producción tesistica regional es notable: ~340 geositios identificados en 21 tesis revisadas, desde Lauca (Cornejo 2019, 19 sitios), Llullaillaco (Alegre 2017, 5), Caldera-Copiapó (Travella 2021, 15; libro Abad et al. 2022 con 27 geositios y 7 rutas), Petorca (Pérez 2018, 12), Puchuncaví (López 2016, 5), Santiago urbano (Rodríguez 2013, 31), Altos de Lircay (Celedón 2021, 6), Nevados de Chillán (Rivera 2014, 11; Urrutia 2018, 30), Puerto Varas (Martínez 2017, 11), Kütralkura (Partarrieu 2013, 24; Martínez 2010, 29; Zapata 2021, 33), Cerro Castillo (Aravena 2014, 5), Lago General Carrera (Valenzuela 2017, 16), Exploradores-Leones (Andrade 2018, 16), Pali Aike (Mardones 2012, 6) y Torres del Paine (Fernández 2007, 21). Hay un Geoparque UNESCO consolidado (Kütralkura, 8.100 km², Araucanía) y proyectos en curso (Cajón del Maipo, Puchuncaví, Petorca, Pillanmapu en el Maule, Atacama).

**Lo que falta.** Tres de los 22 contextos siguen sin representación: Arco volcánico del Mesozoico (AcMz), Islas y pisos oceánicos (IO) y Campos de hielo e inlandsis Antártico (CHA). El sistema chileno carece de un equivalente a la Ley 42/2007 española: no existe obligación legal de elaborar un Inventario Nacional de LIGs ni protección automática para sitios catalogados (Geoconservación Chile 2018). La articulación institucional entre SERNAGEOMIN, SGCh, CMN, MMA, CONAF e INACH es débil, con superposición de Santuarios de la Naturaleza, ZOIT y figuras SBAP. Casos paradigmáticos como El Laco y Lastarria (Guijón et al. 2011) siguen sin protección formal pese a su valor mundial. La distribución es desigual: Aysén concentra 21 geositios SGCh formales (Benado 2020), mientras regiones enteras (Tarapacá, Ñuble, Los Ríos) tienen muy pocos.

**El cuello de botella real.** Chile tiene ciencia y catastro; lo que no tiene es producto ciudadano. No hay un visor nacional unificado de geositios con fichas accesibles, no hay programa de ciencia ciudadana al estilo "Apadrina una Roca" (Cabrera et al. 2019), ni etiquetado para emprendedores rurales tipo "Accueil paysan" francés (Corcuera 2016). La brecha es de interfaz, gobernanza local y producto turístico, no de datos crudos.

---

## 2. Ideas de productos digitales (visor)

1. **Capa "22 Contextos Geológicos" como filtro maestro.** Cada uno de los 49 geositios SERNAGEOMIN + ~340 de tesis se etiqueta con su código (MgPz, MgMz, MgVCz, AcMz, VNgsQ, IO, TCA, SSPz, SCMz, SMTrJ, SMKi, KsMC, SCCz, SMCz, AFNgQ, BC, DA, PGGl, ACQ, CHA, TEC, As). Permite ver instantáneamente los tres contextos sin representación (AcMz, IO, CHA) y priorizar terreno.

2. **Módulo "Apadrina un Geositio Chile".** Réplica directa del programa español IELIG (Cabrera et al. 2019): registro web de voluntarios, formulario de alerta con 5 categorías (favorable / favorable con alteraciones / alterado / degradado / fuertemente degradado), foto-monitoreo con timestamp. Piloto: 10 geositios urbanos accesibles (Cerro Santa Lucía, Granito Orbicular Caldera, La Portada, Capillas de Mármol, Cobquecura, Saltos del Petrohué, Pali Aike, Cerro Renca, Tafonis La Palomera, Glaciar La Paloma).

3. **Fichas con narrativa biogeocultural integrada.** Modelo Manríquez et al. 2019 (Atacama): cada ficha incluye dimensión geológica + biótica + cultural mapuche/atacameña/rapanui + uso histórico. Ejemplo Rapa Nui: ahu, surgencias costeras (DiNapoli et al. 2019) y volcanismo de hot-spot en una sola ficha.

4. **Capa de peligros y riesgo de degradación.** Importar el Mapa de Peligros Volcánicos 1:500.000 de Patagonia Verde (Schilling et al. 2020) y los casos clásicos: lahares Calbuco/Las Cascadas, remoción Villa Santa Lucía 2017, GLOF lago Mapuche (Andrade 2018), grass-flow Chislluma 2001 (Naranjo y Clavero 2005). Útil para SERNATUR y municipios.

5. **Tours virtuales KMZ.** Modelo Tavani et al. 2020 (Zagros / Google Earth) y GSA-NAGT 2020. Tres niveles: escolar, pregrado, avanzado. Empezar con tres áreas con buena exposición: Cordillera Lago General Carrera, Pali Aike, Cajón del Maipo.

6. **Buscador por currículum escolar.** Cada geositio etiquetado por OA de las Bases Curriculares chilenas, eje "Ciencias de la Tierra y el Universo" y Marco de Sendai (Ojeda et al. 2018). Que un profesor de 7° básico pueda filtrar "geositios cercanos a mi colegio que sirven para enseñar ciclo de las rocas".

7. **API pública + descargas.** GeoJSON, KMZ, CSV de los 49 oficiales + ~340 tesistas. Imitar la transparencia del SNIT/IDE Chile (Atlas 2019). Habilita que terceros (operadores, ONG, escuelas) construyan sus propios productos sin pedir permiso.

8. **Módulo "estado de los 22 contextos"** tipo dashboard: cuántos geositios oficiales por contexto, vacíos, hotspots regionales, % de cobertura. Justifica priorización de campañas.

---

## 3. Ideas de geoturismo y rutas

1. **Ruta de Segerstrom 2.0 (Atacama, 450 km, 4-6 días, dificultad media).** Reactivar la transversa cordillera-mar Caldera–Copiapó–Salar de Maricunga–Ojos del Salado en cuatro tramos con 21 paradas (Cáceres et al. 2011). Articula los tres geositios SGCh ya formales (Granito Orbicular, Caos de Puquios, Quebrada El Carbón) con Bahía Inglesa, Laguna Verde y minería histórica. Producto vendible a turismo de intereses especiales.

2. **Ruta del Hielo y los Mármoles (Aysén, 5 días, dificultad media-alta).** Conexión Capillas de Mármol – Glaciar Exploradores – Valle Leones – Cerro Castillo, integrando los 16 geositios de Andrade 2018 + los 5 de Aravena 2014. Ya existe infraestructura sobre Carretera Austral.

3. **Ruta Volcánica Patagonia Verde (Cochamó-Palena, 21 georrutas operativas).** Adoptar tal cual las 21 georrutas ya documentadas con coordenadas por Schilling et al. 2020. No requiere desarrollo nuevo, solo integración al visor y certificación de guías.

4. **Ruta de las 7 Rutas de Jeinimeni (Aysén).** Las 7 rutas con 28 sitios biogeo del libro Benado et al. 2020 (Patagonia / Lago General Carrera): Pliegue Anticlinal-Diatrema, Piedra del Indio, Cerro Apidame, Antiguo Delta, Valle Lunar–Cueva de las Manos, Mina Ligorio Márquez, Lago Jeinimeni–Valle en U. Conexión binacional con el lado argentino.

5. **Geo-circuito Kütralkura (Araucanía, 33 geositios).** Producto ya existente que solo necesita digitalización y capacitación de guías locales mapuche con relatos culturales (Zapata 2021). 5 paisajes geomorfológicos como hilos narrativos: volcánicas exhumadas, cuaternarias, fluvial, glacial-periglacial, estructural-LOFZ.

6. **Ruta Astrobiológica de Atacama (San Pedro–Tebenquiche–Cejar–La Brava–Socompa, 3 días).** Estromatolitos modernos como análogos de Tierra primitiva (Farías y Contreras 2018; Contreras y Farías 2017). Producto premium para turismo científico internacional. Categorización CAT 0-III ya existe para priorizar sitios.

7. **Ruta Urbana Santiago Geológico (1 día, accesible 7 millones de habitantes).** Articular los 31 geositios urbanos y peri-urbanos de Rodríguez 2013: Cerro Santa Lucía (basaltos columnares) – Cerro Renca – Ignimbrita Pudahuel – Cerro Chena – Tafonis La Palomera. Producto escolar de bajísimo costo.

8. **Ruta de Darwin Atacama (Caldera–Bahía Inglesa–terrazas marinas).** Producto ya esbozado en libro Copiapó 2022 (ruta 4 "Ruta de Darwin"): liga el viaje de Beagle 1834-1835 con paleontología miocénica (Cerro Ballena, Pelagornis, Thalasochnus). Storytelling histórico potente.

---

## 4. Ideas de educación y divulgación

1. **"Apadrina una Roca Chile".** Pilotear con 5 colegios y 5 geositios (uno por macrozona). Adaptación literal del programa español de Cabrera et al. 2019.

2. **Mundos Minecraft chilenos.** Replicar Diez-Herrero et al. 2019 con cuatro LIGs: Torres del Paine (laccolito + glaciares), Capillas de Mármol, Volcán Osorno (lavas pahoehoe), Bosque Petrificado. Servidor gratuito SERNAGEOMIN-Explora.

3. **Salidas de campo virtuales KMZ.** Tres niveles según Tavani et al. 2020. Sirve para escuelas rurales sin acceso físico al terreno y para cubrir restricciones presupuestarias.

4. **Unidades didácticas alineadas a 22 contextos.** Una guía de aula por contexto, en formato similar al utilizado por el Geoparque Villuercas-Ibores-Jara (Barrera 2014) con su unidad didáctica para colegios. Distribución gratuita a través de Explora-CONICYT.

5. **Diplomado de guía geoturístico local.** Modelo Geoparque Kütralkura ya en operación. Replicar en Aysén, Petorca, Cajón del Maipo y Puchuncaví. Capacita arrieros, lancheros y operadores rurales con contenido geológico básico (formato Ólafsdóttir 2019, geoturismo a caballo y bicicleta).

6. **Bienal de Geopatrimonio Chileno.** Inspirada en la Bienal RSEHN brasileña-española (Díaz-Acha et al. 2019). Sede rotativa, articula SGCh + universidades + comunidades.

7. **Día Internacional de la Geodiversidad (6 octubre).** Programa anual coordinado SERNAGEOMIN + SGCh con jornadas abiertas en los 49 geositios oficiales (Brilha et al. 2020). Coincide ya con la celebración UNESCO.

8. **Cursos para profesores rurales.** Articular geopatrimonio con cultura de prevención de desastres (Marco de Sendai), siguiendo Ojeda et al. 2018. Piloto en escuelas cercanas a Calbuco, Llaima y Villarrica.

---

## 5. Ideas de gestión y políticas

1. **Validar oficialmente los 22 contextos.** Hoy son una propuesta SGCh 2012 / paper 2016 sin estatus normativo. Una resolución SERNAGEOMIN que los oficialice como base del Inventario Nacional cierra el lazo entre Mourgues 2016 y producto público.

2. **Ley de Patrimonio Geológico.** Inspirada en la Ley 42/2007 española (Díaz-Martínez et al. 2008): obligación de Inventario Nacional de LIGs, anexo de contextos geológicos relevantes, mecanismo de protección automática post-inventario. Indispensable para cerrar el caso El Laco/Lastarria.

3. **Hoja de ruta de geoparques aspirantes.** Definir cohorte 2026-2030: Cajón del Maipo (libro Estay 2021), Puchuncaví (López 2016), Petorca (Pérez 2018), Pillanmapu-Maule (Stefani 2023), Atacama (libro Copiapó 2022). Cada uno con plazos y financiamiento FNDR.

4. **Protocolo de protección de secciones tipo.** Adaptar Brocx, Brown y Semeniuk 2019: catastro nacional de localidades tipo, GSSPs y estratotipos chilenos como categoría especial del visor con protección diferenciada. Empezar con Localidad Tipo Formación Lo Prado, Caleta Herradura, Bahía Inglesa.

5. **Mesa interinstitucional permanente** SERNAGEOMIN–SGCh–CONAF–CMN–MMA–SERNATUR–SUBDERE. Modelo de gobernanza horizontal Villuercas (Barrera 2017) con plan estratégico anual co-financiado.

---

## 6. Ideas para comunidades locales

1. **Etiqueta "Anfitrión Geoturístico Chile".** Réplica del "Accueil paysan" francés (Corcuera 2016) y de Geovilluercas (Barrera 2014). Certificación voluntaria a alojamientos y operadores rurales que cumplan: capacitación básica, materiales de interpretación, seguimiento de capacidad de carga. Permite cobrar premium sin cambiar la oferta.

2. **Producto turístico participativo.** Aplicar las 8 etapas Ramírez 2019 (sensibilización → contextualización → diseño → demanda → precio → comercialización → prueba → seguimiento) en pilotos comunales (ej. Caldera, Lonquimay, Chile Chico, Cochamó). Evita el extractivismo turístico.

3. **Coexistencia con minería.** Los geositios de El Laco, Mina Algarrobo, Mina San José (Atacama), Lo Aguirre, Naltagua (RM) y Cerro Bayo (Aysén) demuestran que el patrimonio minero histórico es un activo turístico, no un pasivo. Generar protocolo SERNAGEOMIN–SONAMI de geositios mineros con visita guiada y cierre seguro.

4. **Museos comunales pequeños.** Modelo Caldera (Griem 2014) y Pilauco-Osorno: una sala municipal con piezas locales bien interpretadas vale más que un megamuseo lejano. Subsidio SUBDERE de M$30-50 millones por sala.

5. **Anticipar conflictos discursivos.** Aplicar etnografía previa a la declaratoria (Valcuende et al. 2011). En Atacama (lickanantay), Araucanía (mapuche pewenche) y Rapa Nui esto es crítico: la "naturaleza" geológica científica no es la única en juego.

---

## 7. Quick wins inmediatos (<1 mes)

1. **Importar al visor los 49 geositios SERNAGEOMIN 2024 + 27 del libro Copiapó 2022 + 33 de Kütralkura + 21 de Torres del Paine + 16 de Valenzuela 2017.** Da una primera capa con ~146 geositios cargados, suficiente para comunicar. Ya están en los JSON consolidados.

2. **Publicar el dashboard "estado de los 22 contextos".** Con los datos actuales muestra que AcMz, IO y CHA siguen vacíos. Convierte una métrica de gestión en pieza de comunicación.

3. **Subir los 21 georrutas Patagonia Verde (Schilling et al. 2020) como capa KMZ pública.** Datos ya existen, solo requieren integración. Producto descargable para operadores de Cochamó, Hualaihué, Chaitén, Futaleufú, Palena.

4. **Lanzar formulario beta "Reporta tu Geositio".** Versión mínima de Apadrina una Roca: foto + coordenadas + estado en 5 categorías. Difundir entre los 33 guías ya formados de Kütralkura y la red SGCh.

5. **Crear las primeras 5 fichas piloto biogeoculturales** (Capillas de Mármol, El Enladrillado, Cerro Castillo, Saltos del Petrohué, Cerro Santa Lucía) con texto divulgativo de 800 palabras + 1 mapa + 5 fotos + relato cultural. Sirve de plantilla replicable y demuestra el formato a financistas (FNDR, FIC-R, CORFO, FIA).
