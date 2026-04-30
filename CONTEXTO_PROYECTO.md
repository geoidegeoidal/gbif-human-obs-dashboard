# Contexto del Proyecto: Carrusel GBIF Animalia @conmapas

## Resumen del proyecto

Estamos creando un **carrusel de Instagram de 11 slides** para la cuenta **@conmapas** usando datos de ocurrencia del reino Animalia descargados de GBIF para Chile. El enfoque es **metodológico**: no solo mostrar datos bonitos, sino revelar los sesgos y enseñar a filtrar correctamente.

## Dataset

- **Archivo CSV**: `0022205-260226173443078.csv` (~11 GB, tab-separated)
- **Registros**: 20,801,113 filas, 50 columnas
- **Cobertura temporal**: 1635–2026 (concentrado post-2010)
- **Coordenadas**: 99.2% de registros tienen lat/lon

## Hallazgos clave del EDA

Los resultados completos están en dos archivos JSON:
- `eda_results.json` — EDA general (phylum, class, basisOfRecord, distribución temporal, coordenadas)
- `eda_methodological.json` — análisis metodológico profundo

### Datos que importan para las slides

| Métrica | Valor |
|---|---|
| Total registros | 20,801,113 |
| Con coordenadas | 20,636,696 (99.2%) |
| Chordata | 82.6% |
| Arthropoda | 14.8% |
| Sin Class asignada | 40.3% (8.3M) |
| HUMAN_OBSERVATION | 89.7% |
| MACHINE_OBSERVATION | 7.8% |
| PRESERVED_SPECIMEN | 2.0% |
| occurrenceStatus=ABSENT | 1,170,113 (5.6%) |
| FOSSIL_SPECIMEN | 7,379 (incertidumbre prom. 1,949 km) |
| Sin coordinateUncertainty | 95.0% (19.8M) |
| Aves en human obs | 7,701,624 |
| Insecta en human obs | 66,624 |
| Insecta en preserved specimen | 249,197 |

## Entorno virtual

- Ubicación: `.venv/` en la raíz del proyecto
- **Librerías instaladas**: `duckdb`, `polars`, `pyarrow`, `geopandas`, `matplotlib`, `seaborn`, `squarify`, `Pillow`
- `cartopy` y `contextily` NO se pudieron instalar (falta compilador C)

## Estructura de archivos generados

```
c:\JULLOAR-CODE\sp\gbif\
│
├── 0022205-260226173443078.csv       ← Dataset GBIF original (11 GB)
├── .venv\                            ← Entorno virtual Python
│
├── eda_results.json                  ← Resultados EDA general
├── eda_methodological.json           ← Resultados EDA metodológico
├── map_data.parquet                  ← Datos comprimidos para mapas (118 MB)
│
├── eda_01_overview.py                ← Script EDA general
├── eda_02_json.py                    ← Script conversión a JSON
├── eda_03_methodological.py          ← Script EDA metodológico
├── extract_map_data.py               ← Extracción CSV → Parquet
├── export_geoparquet.py              ← Exportación a GeoParquet con geometría
├── reproject_3857.py                 ← Reproyección a Pseudo-Mercator
│
├── slide_01_hook.py                  ← Script slide 1
├── slide_03_treemap_v2.py            ← Script slide 3 (bar chart)
├── slides_export.py                  ← Script principal slides 1,3-8
├── slides_maps.py                    ← Script mapas (no se usa, mapas van en QGIS)
├── generate_pdf.py                   ← Generador del PDF de propuesta
├── propuesta_carrusel_conmapas.pdf   ← PDF con la propuesta completa
│
├── geoparquet\                       ← GeoParquet para QGIS (EPSG:3857)
│   ├── slide_02_raw_all.parquet      ← Todos los datos sin filtrar (20.6M pts, 214 MB)
│   ├── slide_09_phylum.parquet       ← Filtrado PRESENT+no fósiles, col: phylum (19.5M pts)
│   ├── slide_10_class.parquet        ← Filtrado PRESENT+no fósiles, col: class,phylum (19.5M pts)
│   └── slide_11_basis.parquet        ← Filtrado PRESENT+no fósiles, col: basis (19.5M pts)
│
└── slides\                           ← PNGs generados
    ├── slide_01_hook\
    │   ├── slide_01_hook.png         ← Slide completa (fondo oscuro)
    │   └── charts\hook.png           ← Transparente
    ├── slide_03_treemap\
    │   ├── slide_03_treemap.png
    │   └── charts\phylum_bars.png    ← Barras transparente
    ├── slide_04_timeline\
    │   ├── slide_04_timeline.png
    │   └── charts\timeline_area.png
    ├── slide_05_sesgo\
    │   ├── slide_05_sesgo.png
    │   └── charts\basis_of_record_bars.png + aves_vs_insecta.png
    ├── slide_06_absent_fossil\
    │   ├── slide_06_absent_fossil.png
    │   └── charts\absent_fossil_info.png
    ├── slide_07_incertidumbre\
    │   ├── slide_07_incertidumbre.png
    │   └── charts\uncertainty_bars.png
    └── slide_08_checklist\
        ├── slide_08_checklist.png
        └── charts\checklist.png
```

## Estructura del carrusel (11 slides, 3 actos)

### ACT 1 — El impacto
1. **Hook**: "20 MILLONES... ¿qué estamos contando realmente?" ✅ PNG listo
2. **Mapa crudo**: Todos los 20.8M puntos sin filtrar → **pendiente QGIS** (GeoParquet listo)

### ACT 2 — Desmontando los sesgos
3. **¿Qué es Animalia?**: Bar chart horizontal por phylum ✅ PNG listo
4. **Timeline**: Gráfico de área 1970–2024 ✅ PNG listo
5. **Sesgo ciencia ciudadana**: 9/10 human obs, Aves vs Insecta ✅ PNG listo
6. **ABSENT + fósiles**: 1.17M ABSENT, fósiles con 1,949km incertidumbre ✅ PNG listo
7. **Incertidumbre**: 95% sin dato de precisión ✅ PNG listo

### ACT 3 — Los datos limpios
8. **Checklist**: "Antes de mapear, filtra" ✅ PNG listo
9. **Mapa por Phylum**: Colores por phylum → **pendiente QGIS** (GeoParquet listo)
10. **Mapa por Class**: Colores por class, 40.3% gris → **pendiente QGIS** (GeoParquet listo)
11. **Mapa por basisOfRecord**: Colores por fuente → **pendiente QGIS** (GeoParquet listo)

## Paleta de colores

| Nombre | Hex | Uso |
|---|---|---|
| Background | `#0d1117` | Fondo de todas las slides |
| Amber | `#fbbf24` | Números destacados, títulos |
| Cyan | `#22d3ee` | Chordata, human obs, líneas decorativas |
| Magenta | `#e879f9` | Mollusca, preserved specimen |
| Green | `#4ade80` | Insecta, datos buenos |
| Red | `#f87171` | Warnings, ABSENT, incertidumbre |
| White | `#f1f5f9` | Texto principal |
| Gray | `#94a3b8` | Texto secundario |
| Gray dim | `#475569` | Texto muy sutil |

## Lo que falta por hacer

1. **Hacer los 4 mapas en QGIS** (slides 2, 9, 10, 11):
   - Abrir los GeoParquet de `geoparquet/` (ya en EPSG:3857)
   - Recomendación: cuadrícula de densidad a **10 km**
   - Clasificación por **cuantiles** (no intervalos iguales — datos muy sesgados)
   - Misma paleta de colores del carrusel
   - Exportar a 1080×1080 px

2. **Armar en Canva** el carrusel final:
   - Usar los PNGs de `slides/` como base o referencia
   - Los charts transparentes de `charts/` se pueden superponer en Canva
   - Los mapas de QGIS se incorporan como slides 2, 9, 10, 11

## Notas técnicas importantes

- **DuckDB** se usó para queries directas al CSV de 11 GB sin cargarlo en memoria
- Los GeoParquet usan **geopandas** con geometría POINT
- Todos los GeoParquet están en **EPSG:3857** (Pseudo-Mercator)
- El `map_data.parquet` intermedio está en formato tabular (sin geometría, EPSG:4326)
- matplotlib no renderiza emojis de color (aparecen como cuadros) — en Canva se reemplazan
