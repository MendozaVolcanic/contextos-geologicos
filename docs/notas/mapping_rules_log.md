# Auditoría del mapping mapa al millón → 22 contextos chilenos

Total polígonos procesados: **18935**

## Distribución por contexto

| Código | n polígonos | Contexto |
|---|---:|---|
| MgMz | 3491 | Magmatismo Mesozoico |
| AFNgQ | 2921 | Ambientes fluvioaluviales del Neógeno-Cuaternario |
| AcMz | 2032 | Arco volcánico del Mesozoico |
| VNgsQ | 1926 | Volcanismo Neógeno sup-Cuaternario y campos geotermales |
| MgVCz | 1543 | Magmatismo y vulcanismo Cenozoico |
| UNK | 1319 | ? |
| PGGl | 1206 | Procesos, geoformas y depósitos glaciales del centro y sur |
| DA | 1121 | Desierto de Atacama |
| TCA | 1118 | Terrenos exóticos y complejos de acreción |
| SMTrJ | 934 | Cuencas marinas Triásico-Jurásico-Cretácico basal |
| SSPz | 514 | Series sedimentarias del Paleozoico |
| MgPz | 429 | Magmatismo Paleozoico |
| SMKs | 173 | Cretácico Superior marino de Magallanes y Chile central |
| SCCz | 104 | Series continentales cenozoicas y sus fósiles |
| SMKi | 104 | Cuencas marinas del Cretácico Inferior |

## Conteo por regla aplicada

| n | Regla |
|---:|---|
| 3491 | Intrusivo mesozoico → Magmatismo Mesozoico |
| 2032 | Volcánico mesozoico → Arco volcánico Mesozoico |
| 1724 | Sedimentario neógeno → AFNgQ |
| 1259 | Volcánico Mioceno-Plioceno → VNgsQ |
| 1253 | Intrusivo cenozoico → Magmatismo y vulcanismo Cenozoico |
| 1206 | Cuaternario sedimentario lat<-41°S → Glaciales centro-sur |
| 1205 | sin clasificar (era=S I, comp=S I, periodo=S I) |
| 1197 | Cuaternario sedimentario −41 a −28 → Fluvioaluvial |
| 1121 | Cuaternario sedimentario lat>-28°S → Desierto de Atacama |
| 934 | Sedimentario Tr-J → Cuencas marinas Tr-J |
| 705 | Metamórfico paleozoico → Terrenos exóticos y complejos de acreción |
| 667 | Cuaternario volcánico → VNgsQ |
| 429 | Intrusivo paleozoico → Magmatismo Paleozoico |
| 386 | Metamórfico mesozoico → Terrenos exóticos y complejos de acreción |
| 375 | Volcánico paleozoico → SSPz (default) |
| 290 | Volcánico cenozoico (pre-Mioceno) → MgVCz |
| 173 | Cretácico superior marino → SMKs |
| 139 | Sedimentario paleozoico → Series sedimentarias Pz |
| 109 | sin clasificar (era=SIN INFORMACION, comp=Sin Informacion, periodo=Sin Informacion) |
| 104 | Sedimentario cenozoico → Series continentales cenozoicas |
| 104 | Cretácico inferior marino → SMKi |
| 27 | Metamórfico precámbrico → TCA |
| 5 | sin clasificar (era=CENOZOICO, comp=Rocas metamorficas, periodo=Paleogeno) |

## Limitaciones conocidas
- Las reglas no distinguen marino/continental con suficiente precisión sin facies info.
- Contextos #6 IO (islas oceánicas), #16 BC (borde costero), #21 TEC (estructuras), #22 Lss (impactos) no se asignan automáticamente — requieren información geográfica/estructural adicional.
- Contexto #20 CHA (hielo antártico) está mapeado en el procesamiento antártico aparte.
- Felipe: revisar reglas en `scripts/build_chile_contextos.py` función `assign_contexto()`.
