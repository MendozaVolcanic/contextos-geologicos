#!/usr/bin/env bash
# Descarga reproducible de todo el corpus SCAR usado en el análisis bibliométrico.
# Salida: ~66 MB en 4 sub-folders + scar_gazetteer.csv (15 MB).
# Verificado mayo 2026.
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
LIB_DIR="$(cd "$BASE_DIR/.." && pwd)"

mkdir -p "$BASE_DIR/osc" "$BASE_DIR/eg_geocon" "$BASE_DIR/atcm" "$BASE_DIR/papers"

dl() {  # dl <url> <dest>
  local url="$1" dest="$2"
  if [ -s "$dest" ]; then
    echo "  [SKIP] $(basename "$dest") ya existe"
    return
  fi
  echo "  [DL]   $(basename "$dest")"
  curl -L -f -s -o "$dest" "$url"
}

echo "=== SCAR OSC abstract books ==="
dl "https://scar.org/~documents/conferences/scar-open-science-conferences/abstracts/scar-open-science-conference-2024-abstracts?layout=default" "$BASE_DIR/osc/SCAR_OSC_2024_Pucon_abstracts.pdf"
dl "https://scar.org/~documents/conferences/scar-open-science-conferences/abstracts/scar-open-science-conference-2022-abstracts?layout=default" "$BASE_DIR/osc/SCAR_OSC_2022_abstracts.pdf"
dl "https://scar.org/~documents/conferences/scar-open-science-conferences/abstracts/scar-osc-2020-abstracts?layout=default" "$BASE_DIR/osc/SCAR_OSC_2020_abstracts.pdf"
dl "https://scar.org/~documents/conferences/scar-open-science-conferences/abstracts/polar2018-abstracts?layout=default" "$BASE_DIR/osc/POLAR2018_abstracts.pdf"
dl "https://scar.org/~documents/conferences/scar-open-science-conferences/abstracts/polar2018-polarexpo?layout=default" "$BASE_DIR/osc/POLAR2018_PolarExpo_posters.pdf"
dl "https://scar.org/~documents/conferences/scar-open-science-conferences/abstracts/scar-osc-2016-abstracts?layout=default" "$BASE_DIR/osc/SCAR_OSC_2016_abstracts.pdf"
dl "https://scar.org/~documents/conferences/scar-open-science-conferences/abstracts/scar-research-day-2016-abstracts?layout=default" "$BASE_DIR/osc/SCAR_ResearchDay_2016_abstracts.pdf"
dl "https://scar.org/~documents/conferences/scar-open-science-conferences/abstracts/scar-and-comnap-2014-abstracts?layout=default" "$BASE_DIR/osc/SCAR_OSC_2014_COMNAP_abstracts.pdf"
dl "https://scar.org/~documents/conferences/scar-open-science-conferences/abstracts/scar-osc-2012-abstracts?layout=default" "$BASE_DIR/osc/SCAR_OSC_2012_abstracts.pdf"

echo "=== SCAR EG-GEOCON documents ==="
dl "https://scar.org/~documents/policy/antarctic-treaty/atcm-xxxix-and-cep-xix-2016/atcm39-ip031?layout=default" "$BASE_DIR/eg_geocon/ATCM39_IP031_2016_Antarctic_Geoconservation_Review.pdf"
dl "https://scar.org/~documents/policy/antarctic-treaty/atcm-xxxix-and-cep-xix-2016/atcm39-att042?layout=default" "$BASE_DIR/eg_geocon/ATCM39_ATT042_2016_Geoconservation_Attachment.pdf"
dl "https://scar.org/~documents/scar-meeting-papers/scar-excom-2019-plovdiv-bulgaria/sub-group-reports-2019/geoheritage-report-2019?layout=default" "$BASE_DIR/eg_geocon/Geoheritage_AG_Report_2019.pdf"
dl "https://scar.org/~documents/scar-meeting-papers/xxxvii-scar-delegates-2022-goa-india-1/sub-group-reports-2022/geocon-22?layout=default" "$BASE_DIR/eg_geocon/EG-GEOCON_Proposal_2022.pdf"
dl "https://scar.org/~documents/science-4/geosciences/geoconservation/presentation-geoheritage-and-geoconservation-concepts-and-methodology-scar-2024?layout=default" "$BASE_DIR/eg_geocon/Geoheritage_Concepts_Methodology_SCAR2024.pdf"
dl "https://scar.org/~documents/scar-meeting-papers/xxxviii-scar-delegates-2024-punta-arenas-chile/sub-group-reports-2024/eg-geocon-report-2024-1?layout=default" "$BASE_DIR/eg_geocon/EG-GEOCON_Report_2024.pdf"
dl "https://scar.org/~documents/science-4/geosciences/geoconservation/isaes-2025-eg-geocon-presentation?layout=default" "$BASE_DIR/eg_geocon/ISAES_2025_EG-GEOCON.pdf"
dl "https://scar.org/~documents/science-4/geosciences/geoconservation/gf1-mt-riiser-larsen-updated?layout=default" "$BASE_DIR/eg_geocon/Geosite_GF1_Mt_Riiser-Larsen.pdf"
dl "https://scar.org/~documents/science-4/geosciences/geoconservation/gf1-torckler-tang-updated?layout=default" "$BASE_DIR/eg_geocon/Geosite_GF1_Torckler-Tang.pdf"
dl "https://scar.org/~documents/science-4/geosciences/geoconservation/gf1-shcherbinina-layered-complex-updated?layout=default" "$BASE_DIR/eg_geocon/Geosite_GF1_Shcherbinina_Layered_Complex.pdf"
dl "https://scar.org/~documents/science-4/geosciences/geoconservation/gf1-casey-bay-pegmatites-updated?layout=default" "$BASE_DIR/eg_geocon/Geosite_GF1_Casey_Bay_Pegmatites.pdf"
dl "https://scar.org/~documents/science-4/geosciences/geoconservation/gf1-taynaya-paragneiss-updated?layout=default" "$BASE_DIR/eg_geocon/Geosite_GF1_Taynaya_Paragneiss.pdf"
dl "https://scar.org/~documents/science-4/geosciences/geoconservation/gf1-mt-sones-geosite-updated?layout=default" "$BASE_DIR/eg_geocon/Geosite_GF1_Mt_Sones.pdf"
dl "https://scar.org/~documents/science-4/geosciences/geoconservation/gf7-geosite-form-yamato-mntns-updated?layout=default" "$BASE_DIR/eg_geocon/Geosite_GF7_Yamato_Mountains.pdf"
dl "https://scar.org/~documents/science-4/geosciences/geoconservation/monte-flora-poster?layout=default" "$BASE_DIR/eg_geocon/Monte_Flora_Fossils_Poster.pdf"

echo "=== ATCM Working Papers ==="
dl "https://scar.org/~documents/policy/antarctic-treaty/atcm-xliii-and-cep-xxiii-2021-paris-france/atcm43-att100" "$BASE_DIR/atcm/ATCM43_Att-A_2021_Method_Identification_Antarctic_Geological_Sites.pdf"

echo "=== SCAR Composite Gazetteer (15 MB) ==="
if [ ! -s "$LIB_DIR/scar_gazetteer.csv" ]; then
  curl -L -f -s -o "$LIB_DIR/scar_gazetteer.csv" \
    "https://data.aad.gov.au/geoserver/aadc/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=aadc:SCAR_CGA_PLACE_NAMES_SIMPLIFIED&outputFormat=csv"
  echo "  [OK] scar_gazetteer.csv: $(wc -l <"$LIB_DIR/scar_gazetteer.csv") líneas"
else
  echo "  [SKIP] scar_gazetteer.csv ya existe"
fi

echo ""
echo "=== Resumen ==="
total=$(du -ch "$BASE_DIR"/{osc,eg_geocon,atcm}/*.pdf "$LIB_DIR/scar_gazetteer.csv" 2>/dev/null | tail -1 | awk '{print $1}')
echo "Total descargado: $total"
