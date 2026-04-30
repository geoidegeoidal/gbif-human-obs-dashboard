<p align="center">
  <img src="https://img.shields.io/badge/Streamlit-Live-06d6a0?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit Live"/>
  <img src="https://img.shields.io/badge/GBIF-20.8M_records-00b4d8?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgZmlsbD0iIzAwYjRkOCIvPjwvc3ZnPg==&logoColor=white" alt="GBIF"/>
  <img src="https://img.shields.io/badge/Python-3.11+-ffd166?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Plotly-6.7-e040fb?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly"/>
</p>

# 🌊 GBIF Human Observations Dashboard

**Dashboard interactivo de exploración de datos de biodiversidad** para Chile, basado en 20.8 millones de registros del reino Animalia descargados de [GBIF.org](https://www.gbif.org/).

Diseño *Bioluminescence* — inspirado en la luminiscencia de organismos de aguas profundas.

<p align="center">
  <a href="https://gbif-human-obs-dashboard-nnpqgsdq2g2a6h3dxxw5vi.streamlit.app/">
    <strong>🔗 Ver Dashboard en vivo →</strong>
  </a>
</p>

---

## ✨ Características

| Sección | Qué muestra |
|---------|-------------|
| **Resumen** | KPIs principales, mapa de densidad hexbin interactivo (Plotly), clusters neon (Folium), heatmap, distribución por fuente de datos y evolución anual |
| **Taxonomía** | Distribución por phylum y clase, top 15 especies, ratio Aves vs Insecta, análisis de sesgo taxonómico |
| **Espacialidad** | Mapa interactivo con 3 modos de visualización, top provincias, métricas de concentración geográfica |
| **Temporalidad** | Evolución 1950–2025, estacionalidad mensual, hitos clave (eBird, iNaturalist, COVID-19) |
| **Calidad** | Completitud de campos taxonómicos, distribución de incertidumbre de coordenadas, checklist de calidad |
| **Sesgos** | Radar de sesgos (7 dimensiones), comparación HUMAN_OBSERVATION vs PRESERVED_SPECIMEN, guía de interpretación |

### 🗺️ Mapas interactivos

El dashboard ofrece **3 modos de visualización geoespacial**:

- **Hexbin Interactivo** (Plotly) — Hexágonos de densidad con escala cromática bioluminiscente
- **Clusters Neon** (Folium) — Agrupación por proximidad con color dinámico según conteo
- **Densidad Holográfica** (Folium) — Heatmap con gradiente oceánico

---

## 🚀 Deploy

El dashboard está desplegado en **Streamlit Community Cloud** y se actualiza automáticamente al hacer push a `master`.

**URL de producción:**
```
https://gbif-human-obs-dashboard-nnpqgsdq2g2a6h3dxxw5vi.streamlit.app/
```

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Framework | [Streamlit](https://streamlit.io/) ≥ 1.50 |
| Gráficos | [Plotly](https://plotly.com/python/) ≥ 6.0 |
| Mapas | [Folium](https://python-visualization.github.io/folium/) ≥ 0.19 + streamlit-folium ≥ 0.24 |
| Datos | [DuckDB](https://duckdb.org/) ≥ 1.2 (queries directas al CSV de 11 GB) |
| DataFrames | [Pandas](https://pandas.pydata.org/) ≥ 2.0 |
| Tipografías | JetBrains Mono + Inter (Google Fonts) |

---

## 📁 Estructura del Proyecto

```
gbif-human-obs-dashboard/
├── streamlit_app.py              ← App principal (single-file, ~1000 líneas)
├── requirements.txt              ← Dependencias para Streamlit Cloud
├── .streamlit/
│   └── config.toml               ← Tema oscuro + configuración
├── dashboard/
│   ├── data/
│   │   └── precomputed/          ← JSONs y Parquets pre-calculados
│   │       ├── kpi.json
│   │       ├── phylum_human.json
│   │       ├── coords_sample.parquet
│   │       └── ...
│   ├── app.py                    ← Entry point alternativo (modular)
│   ├── config.py
│   ├── style.py
│   ├── components/
│   └── pages/
└── CONTEXTO_PROYECTO.md          ← Documentación del análisis EDA
```

---

## 📊 Datos

| Métrica | Valor |
|---------|-------|
| Registros totales | 20,801,113 |
| Observaciones humanas | 18,662,018 (89.7%) |
| Con coordenadas | 20,636,696 (99.2%) |
| Registros ABSENT | 1,170,113 (5.6%) |
| Phyla detectados | 23 |
| Rango temporal | 1635 – 2026 |
| País | Chile (CL) |
| Reino | Animalia |

**Fuente:** [GBIF.org](https://www.gbif.org/) — DOI de descarga: `0022205-260226173443078`

---

## 🎨 Diseño: Bioluminescence

El concepto visual está inspirado en la **bioluminiscencia oceánica** — organismos de aguas profundas que generan su propia luz. Es una metáfora visual para un dashboard de biodiversidad que ilumina patrones ocultos en datos masivos.

| Elemento | Color | Hex |
|----------|-------|-----|
| Fondo oceánico | Navy profundo | `#020817` |
| Acento primario | Teal bioluminiscente | `#06d6a0` |
| Acento secundario | Magenta de medusa | `#e040fb` |
| Datos numéricos | Ámbar abisal | `#ffd166` |
| Alertas | Coral vivo | `#ef476f` |
| Acento marino | Azul océano | `#00b4d8` |

**Efectos CSS:** glassmorphism con `backdrop-filter: blur`, bordes pulsantes animados, scanlines sutiles, tipografía monospace para datos.

---

## ⚡ Ejecución Local

```bash
# Clonar el repositorio
git clone https://github.com/geoidegeoidal/gbif-human-obs-dashboard.git
cd gbif-human-obs-dashboard

# Crear entorno virtual
python -m venv .venv
.venv/Scripts/activate   # Windows
# source .venv/bin/activate  # macOS/Linux

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run streamlit_app.py
```

---

## 📝 Licencia

Datos de biodiversidad proporcionados por [GBIF.org](https://www.gbif.org/) bajo sus términos de uso.

Proyecto creado por **[@conmapas](https://www.instagram.com/conmapas/)**.
