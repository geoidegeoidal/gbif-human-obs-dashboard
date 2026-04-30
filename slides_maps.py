"""
Map slides for @conmapas carousel.
Slide 2:  Raw map (all points, single color)
Slide 9:  Filtered map colored by Phylum
Slide 10: Filtered map colored by Class
Slide 11: Filtered map colored by basisOfRecord

Uses the pre-extracted map_data.parquet (118 MB, 20.6M rows).
Points are rendered using matplotlib scatter with tiny markers and alpha.
To handle 20M+ points efficiently, we use DuckDB to sample/aggregate.
"""
import duckdb
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
import time

os.makedirs('slides', exist_ok=True)

# --- Style ---
SIZE, DPI = 1080, 150
FIG = SIZE / DPI
BG = '#0d1117'
AMBER = '#fbbf24'
CYAN = '#22d3ee'
MAGENTA = '#e879f9'
GREEN = '#4ade80'
RED = '#f87171'
ORANGE = '#fb923c'
WHITE = '#f1f5f9'
GRAY = '#94a3b8'
GRAY_DIM = '#475569'
DARK = '#1e293b'

con = duckdb.connect()
PQ = 'map_data.parquet'

# Chile extent (generous)
LAT_MIN, LAT_MAX = -56, -17
LON_MIN, LON_MAX = -76, -66

# We'll sample for scatter plots. 20M points in matplotlib = too slow.
# 2M points is enough for visual density at 1080px.
SAMPLE_N = 2_000_000


def chile_basemap(ax):
    """Set up axes for Chile map."""
    ax.set_xlim(LON_MIN, LON_MAX)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.set_facecolor(BG)
    ax.set_aspect('auto')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(GRAY_DIM)
    ax.spines['bottom'].set_color(GRAY_DIM)
    ax.spines['left'].set_alpha(0.3)
    ax.spines['bottom'].set_alpha(0.3)
    ax.tick_params(colors=GRAY_DIM, labelsize=6)
    ax.set_xlabel('')
    ax.set_ylabel('')


def save_fig(fig, name):
    fig.savefig(f'slides/{name}', dpi=DPI, facecolor=BG, bbox_inches='tight', pad_inches=0.05)
    plt.close()
    print(f"  Saved: slides/{name}")


# =================================================================
# SLIDE 2 — Raw map (all points, single color cyan)
# =================================================================
print("Building Slide 2 — Raw map...")
t0 = time.perf_counter()

df = con.sql(f"""
    SELECT lat, lon
    FROM '{PQ}'
    WHERE lat BETWEEN {LAT_MIN} AND {LAT_MAX}
      AND lon BETWEEN {LON_MIN} AND {LON_MAX}
    USING SAMPLE {SAMPLE_N}
""").fetchdf()

fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG), dpi=DPI)
fig.patch.set_facecolor(BG)
chile_basemap(ax)

ax.scatter(df['lon'], df['lat'], s=0.15, c=CYAN, alpha=0.2, linewidths=0, rasterized=True)

# Title
ax.text(0.5, 0.98, 'ASÍ SE VEN 20.8 MILLONES', fontsize=22, fontweight='bold',
        fontfamily='Impact', color=WHITE, ha='center', va='top', transform=ax.transAxes)
ax.text(0.5, 0.93, 'DE REGISTROS SIN FILTRAR', fontsize=18, fontweight='bold',
        fontfamily='Impact', color=GRAY, ha='center', va='top', transform=ax.transAxes)

ax.text(0.5, 0.02, 'Este mapa esconde varios problemas...', fontsize=9,
        fontfamily='Segoe UI', color=GRAY, ha='center', va='bottom',
        transform=ax.transAxes, style='italic', alpha=0.5)
ax.text(0.02, 0.02, '@conmapas', fontsize=8, fontfamily='Segoe UI',
        color=GRAY_DIM, transform=ax.transAxes, alpha=0.4, style='italic')

plt.tight_layout(pad=0.3)
save_fig(fig, 'slide_02_mapa_crudo.png')
print(f"  ({time.perf_counter()-t0:.1f}s, {len(df):,.0f} points)")


# =================================================================
# SLIDE 9 — Filtered map by PHYLUM
# =================================================================
print("\nBuilding Slide 9 — Map by Phylum...")
t0 = time.perf_counter()

phylum_colors = {
    'Chordata': CYAN,
    'Arthropoda': AMBER,
    'Mollusca': MAGENTA,
}

df = con.sql(f"""
    SELECT lat, lon, phylum
    FROM '{PQ}'
    WHERE lat BETWEEN {LAT_MIN} AND {LAT_MAX}
      AND lon BETWEEN {LON_MIN} AND {LON_MAX}
      AND status = 'PRESENT'
      AND basis != 'FOSSIL_SPECIMEN'
    USING SAMPLE {SAMPLE_N}
""").fetchdf()

fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG), dpi=DPI)
fig.patch.set_facecolor(BG)
chile_basemap(ax)

# Plot "Otros" first (background), then major phyla on top
mask_other = ~df['phylum'].isin(phylum_colors.keys()) | df['phylum'].isna()
ax.scatter(df.loc[mask_other, 'lon'], df.loc[mask_other, 'lat'],
           s=0.1, c=GRAY_DIM, alpha=0.1, linewidths=0, rasterized=True)

for phylum, color in reversed(list(phylum_colors.items())):
    mask = df['phylum'] == phylum
    ax.scatter(df.loc[mask, 'lon'], df.loc[mask, 'lat'],
               s=0.15, c=color, alpha=0.2, linewidths=0, rasterized=True)

# Title
ax.text(0.5, 0.98, 'DATOS FILTRADOS', fontsize=16, fontweight='bold',
        fontfamily='Impact', color=GRAY, ha='center', va='top', transform=ax.transAxes)
ax.text(0.5, 0.93, 'POR PHYLUM', fontsize=26, fontweight='bold',
        fontfamily='Impact', color=WHITE, ha='center', va='top', transform=ax.transAxes)

# Legend
legend_y = 0.15
legend_items = [('Chordata (82.6%)', CYAN), ('Arthropoda (14.8%)', AMBER),
                ('Mollusca (1.5%)', MAGENTA), ('Otros / Sin phylum', GRAY_DIM)]
for i, (label, color) in enumerate(legend_items):
    y = legend_y - i * 0.035
    ax.add_patch(mpatches.Circle((0.88, y), 0.008, transform=ax.transAxes,
                 facecolor=color, edgecolor=color, alpha=0.8))
    ax.text(0.85, y, label, fontsize=7, fontfamily='Segoe UI', color=WHITE,
            ha='right', va='center', transform=ax.transAxes, alpha=0.7)

# Null note
ax.text(0.5, 0.02, 'Sin phylum: 7,253 registros (0.03%) · Filtro: PRESENT, sin fósiles',
        fontsize=7, fontfamily='Segoe UI', color=GRAY, ha='center', va='bottom',
        transform=ax.transAxes, alpha=0.4)
ax.text(0.02, 0.02, '@conmapas', fontsize=8, fontfamily='Segoe UI',
        color=GRAY_DIM, transform=ax.transAxes, alpha=0.4, style='italic')

plt.tight_layout(pad=0.3)
save_fig(fig, 'slide_09_mapa_phylum.png')
print(f"  ({time.perf_counter()-t0:.1f}s, {len(df):,.0f} points)")


# =================================================================
# SLIDE 10 — Filtered map by CLASS
# =================================================================
print("\nBuilding Slide 10 — Map by Class...")
t0 = time.perf_counter()

class_colors = {
    'Aves': CYAN,
    'Malacostraca': AMBER,
    'Mammalia': MAGENTA,
    'Insecta': GREEN,
}

df = con.sql(f"""
    SELECT lat, lon, class
    FROM '{PQ}'
    WHERE lat BETWEEN {LAT_MIN} AND {LAT_MAX}
      AND lon BETWEEN {LON_MIN} AND {LON_MAX}
      AND status = 'PRESENT'
      AND basis != 'FOSSIL_SPECIMEN'
    USING SAMPLE {SAMPLE_N}
""").fetchdf()

fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG), dpi=DPI)
fig.patch.set_facecolor(BG)
chile_basemap(ax)

# Plot nulls/others first
mask_null = df['class'].isna() | (df['class'] == '') | (~df['class'].isin(class_colors.keys()))
ax.scatter(df.loc[mask_null, 'lon'], df.loc[mask_null, 'lat'],
           s=0.1, c=GRAY_DIM, alpha=0.1, linewidths=0, rasterized=True)

for cls, color in reversed(list(class_colors.items())):
    mask = df['class'] == cls
    ax.scatter(df.loc[mask, 'lon'], df.loc[mask, 'lat'],
               s=0.15, c=color, alpha=0.25, linewidths=0, rasterized=True)

# Title
ax.text(0.5, 0.98, 'DATOS FILTRADOS', fontsize=16, fontweight='bold',
        fontfamily='Impact', color=GRAY, ha='center', va='top', transform=ax.transAxes)
ax.text(0.5, 0.93, 'POR CLASS', fontsize=26, fontweight='bold',
        fontfamily='Impact', color=WHITE, ha='center', va='top', transform=ax.transAxes)

# Legend
legend_items = [('Aves (37.8%)', CYAN), ('Malacostraca (12.8%)', AMBER),
                ('Mammalia (3.1%)', MAGENTA), ('Insecta (1.7%)', GREEN),
                ('Sin class (40.3%)', GRAY_DIM)]
for i, (label, color) in enumerate(legend_items):
    y = 0.18 - i * 0.035
    ax.add_patch(mpatches.Circle((0.88, y), 0.008, transform=ax.transAxes,
                 facecolor=color, edgecolor=color, alpha=0.8))
    ax.text(0.85, y, label, fontsize=7, fontfamily='Segoe UI', color=WHITE,
            ha='right', va='center', transform=ax.transAxes, alpha=0.7)

# Warning
ax.text(0.5, 0.02, '⚠ 8.3M registros sin Class (40.3%) aparecen en gris',
        fontsize=8, fontfamily='Segoe UI', color=RED, ha='center', va='bottom',
        transform=ax.transAxes, alpha=0.7, fontweight='bold')
ax.text(0.02, 0.02, '@conmapas', fontsize=8, fontfamily='Segoe UI',
        color=GRAY_DIM, transform=ax.transAxes, alpha=0.4, style='italic')

plt.tight_layout(pad=0.3)
save_fig(fig, 'slide_10_mapa_class.png')
print(f"  ({time.perf_counter()-t0:.1f}s, {len(df):,.0f} points)")


# =================================================================
# SLIDE 11 — Filtered map by basisOfRecord
# =================================================================
print("\nBuilding Slide 11 — Map by basisOfRecord...")
t0 = time.perf_counter()

basis_colors = {
    'HUMAN_OBSERVATION': CYAN,
    'MACHINE_OBSERVATION': AMBER,
    'PRESERVED_SPECIMEN': MAGENTA,
}

df = con.sql(f"""
    SELECT lat, lon, basis
    FROM '{PQ}'
    WHERE lat BETWEEN {LAT_MIN} AND {LAT_MAX}
      AND lon BETWEEN {LON_MIN} AND {LON_MAX}
      AND status = 'PRESENT'
      AND basis != 'FOSSIL_SPECIMEN'
    USING SAMPLE {SAMPLE_N}
""").fetchdf()

fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG), dpi=DPI)
fig.patch.set_facecolor(BG)
chile_basemap(ax)

# Others first
mask_other = ~df['basis'].isin(basis_colors.keys())
ax.scatter(df.loc[mask_other, 'lon'], df.loc[mask_other, 'lat'],
           s=0.1, c=GRAY_DIM, alpha=0.1, linewidths=0, rasterized=True)

for basis, color in reversed(list(basis_colors.items())):
    mask = df['basis'] == basis
    ax.scatter(df.loc[mask, 'lon'], df.loc[mask, 'lat'],
               s=0.15, c=color, alpha=0.25, linewidths=0, rasterized=True)

# Title
ax.text(0.5, 0.98, '¿QUIÉN GENERÓ', fontsize=22, fontweight='bold',
        fontfamily='Impact', color=WHITE, ha='center', va='top', transform=ax.transAxes)
ax.text(0.5, 0.93, 'EL DATO?', fontsize=26, fontweight='bold',
        fontfamily='Impact', color=AMBER, ha='center', va='top', transform=ax.transAxes)

# Legend
legend_items = [('Obs. humana (89.7%)', CYAN), ('Obs. máquina (7.8%)', AMBER),
                ('Espécimen (2.0%)', MAGENTA), ('Otros (0.5%)', GRAY_DIM)]
for i, (label, color) in enumerate(legend_items):
    y = 0.15 - i * 0.035
    ax.add_patch(mpatches.Circle((0.88, y), 0.008, transform=ax.transAxes,
                 facecolor=color, edgecolor=color, alpha=0.8))
    ax.text(0.85, y, label, fontsize=7, fontfamily='Segoe UI', color=WHITE,
            ha='right', va='center', transform=ax.transAxes, alpha=0.7)

# Note
ax.text(0.5, 0.02, 'Todos los registros tienen basisOfRecord · Sin nulls · Filtro: PRESENT, sin fósiles',
        fontsize=7, fontfamily='Segoe UI', color=GRAY, ha='center', va='bottom',
        transform=ax.transAxes, alpha=0.4)
ax.text(0.02, 0.02, '@conmapas', fontsize=8, fontfamily='Segoe UI',
        color=GRAY_DIM, transform=ax.transAxes, alpha=0.4, style='italic')

plt.tight_layout(pad=0.3)
save_fig(fig, 'slide_11_mapa_basis.png')
print(f"  ({time.perf_counter()-t0:.1f}s, {len(df):,.0f} points)")


print("\n✅ All map slides generated!")
