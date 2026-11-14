<p align="center">
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-06d6a0?style=for-the-badge&logo=streamlit&logoColor=white" alt="Dashboard Streamlit"/>
  <img src="https://img.shields.io/badge/GBIF-20.8M_records-00b4d8?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgZmlsbD0iIzAwYjRkOCIvPjwvc3ZnPg==&logoColor=white" alt="GBIF"/>
  <img src="https://img.shields.io/badge/Python-3.11+-ffd166?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Plotly-6.7-e040fb?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly"/>
</p>

# 🌊 GBIF Human Observations Dashboard

**Dashboard interactivo de exploración de datos de biodiversidad** para Chile, basado en 20.8 millones de registros del reino Animalia descargados de [GBIF.org](https://www.gbif.org/).

Diseño *Bioluminescence* — inspirado en la luminiscencia de organismos de aguas profundas.

**[Ejecución local](#ejecucion-local) · [Secciones](#secciones) · [Datos y alcance](#datos) · [Diseño](#diseno)**

> **Cómo leerlo:** los registros reflejan esfuerzo de observación y disponibilidad de datos, no una muestra uniforme de la biodiversidad. Un área con más registros no necesariamente tiene mayor abundancia o riqueza de especies.

<p align="center">
  <a href="https://gbif-human-obs-dashboard-nnpqgsdq2g2a6h3dxxw5vi.streamlit.app/">
    <strong>🔗 Ver Dashboard en vivo →</strong>
  </a>
</p>

---

<a id="ejecucion-local"></a>
## ⚡ Ejecución local

Usa **Python 3.11** como referencia, coherente con el entorno de desarrollo del repositorio.

```bash
git clone https://github.com/geoidegeoidal/gbif-human-obs-dashboard.git
cd gbif-human-obs-dashboard
python -m venv .venv
```

Activa el entorno según tu terminal:

| Terminal | Comando |
| :--- | :--- |
| PowerShell (Windows) | `.venv\Scripts\Activate.ps1` |
| cmd (Windows) | `.venv\Scripts\activate.bat` |
| macOS / Linux | `source .venv/bin/activate` |

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Abre la dirección que muestre Streamlit, normalmente **http://localhost:8501**. El punto de entrada anterior utiliza los JSON y el Parquet precalculados incluidos en [`dashboard/data/precomputed/`](dashboard/data/precomputed/): **no requiere el CSV original de 20,8 millones de registros para consultar el dashboard**.

---

<a id="secciones"></a>
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

El enlace de producción del proyecto corresponde a **Streamlit Community Cloud**. Para un despliegue propio, selecciona `streamlit_app.py` como punto de entrada y `requirements.txt` como dependencias. La rama conectada y la actualización automática dependen de la configuración de la aplicación en Streamlit Cloud.

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
| Preparación de datos | [DuckDB](https://duckdb.org/) ≥ 1.2 para los análisis sobre el CSV original |
| DataFrames | [Pandas](https://pandas.pydata.org/) ≥ 2.0 |
| Tipografías | JetBrains Mono + Inter (Google Fonts) |

---

## 📁 Estructura del Proyecto

```
gbif-human-obs-dashboard/
├── streamlit_app.py              ← App principal; lee datos precalculados
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

<a id="datos"></a>
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

**Fuente:** [GBIF.org](https://www.gbif.org/) — identificador de descarga utilizado por el proyecto: `0022205-260226173443078`. No es un DOI; consulta la cita de la descarga en GBIF antes de reutilizarla en una publicación.

| Quieres… | Insumos necesarios |
| :--- | :--- |
| Consultar el dashboard | Archivos precalculados incluidos en el repositorio |
| Repetir o modificar el análisis original | CSV de descarga externo y los scripts de preparación/EDA |

Los conteos de esta tabla describen el conjunto analizado, no una consulta en tiempo real a GBIF. El mapa usa una muestra de coordenadas (`coords_sample.parquet`), no todos los registros originales. El CSV original no está versionado en este repositorio.

---

<a id="diseno"></a>
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

## 📝 Licencia

Datos de biodiversidad proporcionados por [GBIF.org](https://www.gbif.org/) bajo sus términos de uso.

Proyecto creado por **[@conmapas](https://www.instagram.com/conmapas/)**.
