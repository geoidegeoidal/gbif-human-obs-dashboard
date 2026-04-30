"""
Slides 3-8: Data visualization slides for the @conmapas carousel.
All slides use data from eda_results.json and eda_methodological.json.
Style: dark background, neon colors, Impact/Segoe UI fonts.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json
import os

os.makedirs('slides', exist_ok=True)

# --- Load data ---
with open('eda_results.json', 'r', encoding='utf-8') as f:
    eda = json.load(f)
with open('eda_methodological.json', 'r', encoding='utf-8') as f:
    meth = json.load(f)

# --- Style constants ---
SIZE, DPI = 1080, 150
FIG = SIZE / DPI
BG = '#0d1117'
AMBER = '#fbbf24'
CYAN = '#22d3ee'
MAGENTA = '#e879f9'
GREEN = '#4ade80'
RED = '#f87171'
WHITE = '#f1f5f9'
GRAY = '#94a3b8'
GRAY_DIM = '#475569'
DARK = '#1e293b'


def new_fig():
    fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG), dpi=DPI)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    return fig, ax


def save_fig(fig, name):
    fig.savefig(f'slides/{name}', dpi=DPI, facecolor=BG, bbox_inches='tight', pad_inches=0.05)
    plt.close()
    print(f"  Saved: slides/{name}")


# =================================================================
# SLIDE 3 — Treemap: ¿Qué es Animalia?
# =================================================================
print("Building Slide 3 — Treemap Animalia...")
fig, ax = new_fig()
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Title
ax.text(0.50, 0.95, '@conmapas', fontsize=10, fontfamily='Segoe UI',
        color=GRAY, ha='center', alpha=0.4, style='italic')
ax.text(0.50, 0.88, 'ANIMALIA ≠', fontsize=38, fontweight='bold',
        fontfamily='Impact', color=AMBER, ha='center')
ax.text(0.50, 0.82, 'SOLO LOS ANIMALES QUE IMAGINAS', fontsize=22, fontweight='bold',
        fontfamily='Impact', color=WHITE, ha='center')

# Treemap-like blocks
phyla = eda['phylum_top15']
total = sum(p['n'] for p in phyla)
block_data = [
    ('Chordata\n82.6%', phyla[0]['n'] / total, CYAN, 0.08, 0.28, 0.55, 0.45),
    ('Arthropoda\n14.8%', phyla[1]['n'] / total, AMBER, 0.08, 0.18, 0.55, 0.09),
    ('Mollusca\n1.5%', phyla[2]['n'] / total, MAGENTA, 0.65, 0.55, 0.30, 0.18),
    ('Otros\n23 phyla', 0.02, GRAY_DIM, 0.65, 0.28, 0.30, 0.25),
]

for label, frac, color, x, y, w, h in block_data:
    rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01",
                                    facecolor=color, alpha=0.25, edgecolor=color, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, fontsize=14, fontweight='bold',
            fontfamily='Segoe UI', color=WHITE, ha='center', va='center')

# Warning box
ax.add_patch(mpatches.FancyBboxPatch((0.06, 0.06), 0.88, 0.09, boxstyle="round,pad=0.01",
             facecolor=RED, alpha=0.1, edgecolor=RED, linewidth=1))
ax.text(0.50, 0.105, '⚠ 40.3% de registros sin Class asignada (8.3M)', fontsize=12,
        fontfamily='Segoe UI', color=RED, ha='center', va='center', fontweight='bold')

# Subtitle
ax.text(0.50, 0.76, 'El Taxonomic Backbone de GBIF incluye desde ballenas hasta tardígrados',
        fontsize=10, fontfamily='Segoe UI', color=GRAY, ha='center', alpha=0.6)

save_fig(fig, 'slide_03_treemap.png')


# =================================================================
# SLIDE 4 — Timeline: Explosión de datos
# =================================================================
print("Building Slide 4 — Timeline...")
fig, ax = new_fig()

years_data = eda['year_dist']
years = [d['year'] for d in years_data]
counts = [d['n'] for d in years_data]

# Area chart
ax.fill_between(years, counts, alpha=0.3, color=CYAN)
ax.plot(years, counts, color=CYAN, linewidth=2, alpha=0.9)

# Style
ax.set_facecolor(BG)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(GRAY_DIM)
ax.spines['bottom'].set_color(GRAY_DIM)
ax.tick_params(colors=GRAY, labelsize=8)
ax.yaxis.set_major_formatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K')
ax.set_xlim(1970, 2025)
ax.set_ylim(0, max(counts) * 1.15)

# Annotation: eBird + iNaturalist
ax.annotate('eBird +\niNaturalist', xy=(2010, 801414), xytext=(1985, 1500000),
            fontsize=10, fontfamily='Segoe UI', color=AMBER, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=AMBER, lw=1.5),
            ha='center')

# Peak annotation
peak_year = years[np.argmax(counts)]
peak_val = max(counts)
ax.annotate(f'{peak_val/1e6:.1f}M', xy=(peak_year, peak_val),
            xytext=(peak_year - 5, peak_val + 100000),
            fontsize=9, fontfamily='Segoe UI', color=CYAN, fontweight='bold', ha='center')

# Title (inside the plot area, top)
ax.text(0.5, 0.97, 'DE 5.000 A 1.8 MILLONES', fontsize=28, fontweight='bold',
        fontfamily='Impact', color=WHITE, ha='center', va='top', transform=ax.transAxes)
ax.text(0.5, 0.89, 'DE REGISTROS POR AÑO', fontsize=22, fontweight='bold',
        fontfamily='Impact', color=GRAY, ha='center', va='top', transform=ax.transAxes)

# Bottom text
ax.text(0.5, 0.05, '2020–2024 = 7.8M registros (38% del total)', fontsize=9,
        fontfamily='Segoe UI', color=GRAY, ha='center', va='bottom', transform=ax.transAxes, alpha=0.6)

ax.text(0.01, 0.01, '@conmapas', fontsize=8, fontfamily='Segoe UI',
        color=GRAY_DIM, va='bottom', transform=ax.transAxes, alpha=0.4, style='italic')
ax.text(0.99, 0.01, 'Fuente: GBIF.org', fontsize=7, fontfamily='Segoe UI',
        color=GRAY_DIM, ha='right', va='bottom', transform=ax.transAxes, alpha=0.3)

plt.tight_layout(pad=0.8)
save_fig(fig, 'slide_04_timeline.png')


# =================================================================
# SLIDE 5 — Sesgo Ciencia Ciudadana
# =================================================================
print("Building Slide 5 — Sesgo ciencia ciudadana...")
fig, ax = new_fig()
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

ax.text(0.50, 0.95, '@conmapas', fontsize=10, fontfamily='Segoe UI',
        color=GRAY, ha='center', alpha=0.4, style='italic')
ax.text(0.50, 0.88, '9 DE CADA 10 REGISTROS', fontsize=30, fontweight='bold',
        fontfamily='Impact', color=WHITE, ha='center')
ax.text(0.50, 0.82, 'SON OBSERVACIONES HUMANAS', fontsize=24, fontweight='bold',
        fontfamily='Impact', color=CYAN, ha='center')

# Horizontal bars for basisOfRecord
basis_data = [
    ('HUMAN_OBSERVATION', 18662018, CYAN),
    ('MACHINE_OBSERVATION', 1618695, AMBER),
    ('PRESERVED_SPECIMEN', 424615, MAGENTA),
    ('Otros', 95785, GRAY_DIM),
]
total_b = sum(b[1] for b in basis_data)
y_pos = 0.72
bar_height = 0.04
for label, n, color in basis_data:
    width = (n / total_b) * 0.80
    rect = mpatches.FancyBboxPatch((0.08, y_pos), width, bar_height, boxstyle="round,pad=0.005",
                                    facecolor=color, alpha=0.6, edgecolor=color, linewidth=0.5)
    ax.add_patch(rect)
    pct = n / total_b * 100
    ax.text(0.08 + width + 0.02, y_pos + bar_height / 2,
            f'{pct:.1f}%', fontsize=9, fontfamily='Segoe UI', color=color,
            va='center', fontweight='bold')
    ax.text(0.06, y_pos + bar_height / 2, label.replace('_', ' ').title(),
            fontsize=8, fontfamily='Segoe UI', color=GRAY, va='center', ha='right')
    y_pos -= 0.065

# Separator
ax.plot([0.08, 0.92], [0.50, 0.50], color=GRAY_DIM, linewidth=0.5, alpha=0.3)

# Comparison: Aves vs Insecta in human observation
ax.text(0.50, 0.46, 'EN OBSERVACIÓN HUMANA:', fontsize=14, fontweight='bold',
        fontfamily='Impact', color=WHITE, ha='center')

# Aves bar
ax.add_patch(mpatches.FancyBboxPatch((0.08, 0.38), 0.80, 0.04, boxstyle="round,pad=0.005",
             facecolor=CYAN, alpha=0.5, edgecolor=CYAN, linewidth=0.5))
ax.text(0.10, 0.40, '🦅 Aves: 7.7M (41%)', fontsize=11, fontfamily='Segoe UI',
        color=WHITE, va='center', fontweight='bold')

# Insecta bar (tiny)
ax.add_patch(mpatches.FancyBboxPatch((0.08, 0.31), 0.80 * (66624/7701624), 0.04, boxstyle="round,pad=0.005",
             facecolor=GREEN, alpha=0.5, edgecolor=GREEN, linewidth=0.5))
ax.text(0.10, 0.33, '🪲 Insecta: 67K (0.4%)', fontsize=11, fontfamily='Segoe UI',
        color=GREEN, va='center', fontweight='bold')

# Contrast insight
ax.add_patch(mpatches.FancyBboxPatch((0.06, 0.16), 0.88, 0.10, boxstyle="round,pad=0.01",
             facecolor=AMBER, alpha=0.08, edgecolor=AMBER, linewidth=1))
ax.text(0.50, 0.23, 'Pero en museos: Insecta = 249K especímenes', fontsize=11,
        fontfamily='Segoe UI', color=AMBER, ha='center', fontweight='bold')
ax.text(0.50, 0.19, '"Los insectos se conocen por museos, no por ciencia ciudadana"', fontsize=9,
        fontfamily='Segoe UI', color=GRAY, ha='center', style='italic')

# Source
ax.text(0.50, 0.04, 'Fuente: GBIF.org · Reino Animalia · Chile', fontsize=7,
        fontfamily='Segoe UI', color=GRAY_DIM, ha='center', alpha=0.3)

save_fig(fig, 'slide_05_sesgo.png')


# =================================================================
# SLIDE 6 — ABSENT + Fósiles
# =================================================================
print("Building Slide 6 — ABSENT + Fósiles...")
fig, ax = new_fig()
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

ax.text(0.50, 0.95, '@conmapas', fontsize=10, fontfamily='Segoe UI',
        color=GRAY, ha='center', alpha=0.4, style='italic')
ax.text(0.50, 0.88, '1.17 MILLONES', fontsize=42, fontweight='bold',
        fontfamily='Impact', color=RED, ha='center')
ax.text(0.50, 0.81, 'DE REGISTROS DICEN "AUSENTE"', fontsize=24, fontweight='bold',
        fontfamily='Impact', color=WHITE, ha='center')

# ABSENT box
ax.add_patch(mpatches.FancyBboxPatch((0.06, 0.55), 0.88, 0.20, boxstyle="round,pad=0.015",
             facecolor=RED, alpha=0.08, edgecolor=RED, linewidth=1.5))
ax.text(0.50, 0.72, '🚫 occurrenceStatus = ABSENT', fontsize=16, fontweight='bold',
        fontfamily='Segoe UI', color=RED, ha='center')
ax.text(0.50, 0.66, '1,170,113 registros (5.6%)', fontsize=14,
        fontfamily='Segoe UI', color=WHITE, ha='center')
ax.text(0.50, 0.60, '"Fuimos, buscamos, y NO encontramos el animal"', fontsize=10,
        fontfamily='Segoe UI', color=GRAY, ha='center', style='italic')
ax.text(0.50, 0.57, 'Si no filtras, lo cuentas erróneamente como presencia', fontsize=9,
        fontfamily='Segoe UI', color=GRAY, ha='center', alpha=0.7)

# FOSSIL box
ax.add_patch(mpatches.FancyBboxPatch((0.06, 0.26), 0.88, 0.22, boxstyle="round,pad=0.015",
             facecolor=AMBER, alpha=0.08, edgecolor=AMBER, linewidth=1.5))
ax.text(0.50, 0.44, '🦴 basisOfRecord = FOSSIL_SPECIMEN', fontsize=16, fontweight='bold',
        fontfamily='Segoe UI', color=AMBER, ha='center')
ax.text(0.50, 0.38, '7,379 registros', fontsize=14,
        fontfamily='Segoe UI', color=WHITE, ha='center')
ax.text(0.50, 0.34, 'Incertidumbre promedio: 1,949 km 💀', fontsize=12,
        fontfamily='Segoe UI', color=AMBER, ha='center', fontweight='bold')
ax.text(0.50, 0.30, '"Moluscos del Mesozoico aparecen como puntos', fontsize=9,
        fontfamily='Segoe UI', color=GRAY, ha='center', style='italic')
ax.text(0.50, 0.275, 'en el Desierto de Atacama actual"', fontsize=9,
        fontfamily='Segoe UI', color=GRAY, ha='center', style='italic')

# Bottom
ax.text(0.50, 0.08, 'Si haces un SDM o análisis de biodiversidad actual,', fontsize=10,
        fontfamily='Segoe UI', color=WHITE, ha='center')
ax.text(0.50, 0.05, 'estos registros generan ruido geoespacial absurdo', fontsize=10,
        fontfamily='Segoe UI', color=RED, ha='center', fontweight='bold')

save_fig(fig, 'slide_06_absent_fossil.png')


# =================================================================
# SLIDE 7 — Incertidumbre de coordenadas
# =================================================================
print("Building Slide 7 — Incertidumbre...")
fig, ax = new_fig()

unc = meth['coord_uncertainty']
categories = ['Sin dato', '≤ 10m', '10-100m', '100m-1km', '1-10km', '10-100km', '>100km']
values = [unc['sin_incertidumbre'], unc['hasta_10m'], unc['10_100m'],
          unc['100_1000m'], unc['1_10km'], unc['10_100km'], unc['mas_100km']]
colors_bar = [RED, GREEN, GREEN, CYAN, AMBER, MAGENTA, RED]

y_positions = np.arange(len(categories))
max_val = max(values)
bar_widths = [v / max_val for v in values]

ax.barh(y_positions, bar_widths, height=0.6, color=colors_bar, alpha=0.6, edgecolor=colors_bar, linewidth=0.5)

# Labels
for i, (cat, val) in enumerate(zip(categories, values)):
    pct = val / unc['total'] * 100
    ax.text(-0.02, i, cat, fontsize=9, fontfamily='Segoe UI',
            color=GRAY, ha='right', va='center')
    if pct >= 1:
        label = f'{pct:.1f}%  ({val/1e6:.1f}M)'
    else:
        label = f'{pct:.1f}%  ({val:,.0f})'
    ax.text(bar_widths[i] + 0.02, i, label, fontsize=8, fontfamily='Segoe UI',
            color=WHITE, ha='left', va='center')

ax.set_facecolor(BG)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
ax.set_xlim(-0.35, 1.4)
ax.invert_yaxis()

# Title
ax.text(0.5, 1.08, '95% DE LOS REGISTROS', fontsize=28, fontweight='bold',
        fontfamily='Impact', color=RED, ha='center', transform=ax.transAxes)
ax.text(0.5, 1.01, 'NO REPORTAN SU PRECISIÓN', fontsize=24, fontweight='bold',
        fontfamily='Impact', color=WHITE, ha='center', transform=ax.transAxes)

# Bottom stats
ax.text(0.5, -0.08, f'Mediana: 1 km · Máximo: 7,945 km · Promedio: 6.5 km',
        fontsize=9, fontfamily='Segoe UI', color=GRAY, ha='center', transform=ax.transAxes)

ax.text(0.01, -0.13, '@conmapas', fontsize=8, fontfamily='Segoe UI',
        color=GRAY_DIM, transform=ax.transAxes, alpha=0.4, style='italic')
ax.text(0.99, -0.13, 'Fuente: GBIF.org', fontsize=7, fontfamily='Segoe UI',
        color=GRAY_DIM, ha='right', transform=ax.transAxes, alpha=0.3)

plt.tight_layout(pad=1.2)
save_fig(fig, 'slide_07_incertidumbre.png')


# =================================================================
# SLIDE 8 — Checklist Metodológico
# =================================================================
print("Building Slide 8 — Checklist...")
fig, ax = new_fig()
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

ax.text(0.50, 0.95, '@conmapas', fontsize=10, fontfamily='Segoe UI',
        color=GRAY, ha='center', alpha=0.4, style='italic')
ax.text(0.50, 0.87, 'ANTES DE MAPEAR', fontsize=38, fontweight='bold',
        fontfamily='Impact', color=CYAN, ha='center')
ax.text(0.50, 0.80, 'FILTRA', fontsize=50, fontweight='bold',
        fontfamily='Impact', color=AMBER, ha='center')

# Checklist items
items = [
    ('✅', 'Filtrar occurrenceStatus = PRESENT', WHITE, GREEN),
    ('✅', 'Excluir FOSSIL_SPECIMEN', WHITE, GREEN),
    ('✅', 'Revisar coordinateUncertaintyInMeters', WHITE, GREEN),
    ('✅', 'Separar por basisOfRecord según tu pregunta', WHITE, GREEN),
    ('⚠️', 'Animalia incluye 27+ phyla, no solo vertebrados', WHITE, AMBER),
]

y_start = 0.67
for i, (icon, text, text_color, accent_color) in enumerate(items):
    y = y_start - i * 0.09
    # Background box
    ax.add_patch(mpatches.FancyBboxPatch((0.06, y - 0.025), 0.88, 0.06,
                 boxstyle="round,pad=0.008", facecolor=accent_color, alpha=0.06,
                 edgecolor=accent_color, linewidth=0.8))
    ax.text(0.10, y + 0.005, icon, fontsize=16, ha='center', va='center',
            fontfamily='Segoe UI Emoji')
    ax.text(0.15, y + 0.005, text, fontsize=11, fontfamily='Segoe UI',
            color=text_color, va='center')

# Bottom quote
ax.plot([0.15, 0.85], [0.18, 0.18], color=CYAN, linewidth=1, alpha=0.3)
ax.text(0.50, 0.13, '"Un dato sin contexto', fontsize=16, fontweight='bold',
        fontfamily='Segoe UI', color=WHITE, ha='center')
ax.text(0.50, 0.09, 'es un mapa que miente"', fontsize=16, fontweight='bold',
        fontfamily='Segoe UI', color=CYAN, ha='center')

ax.text(0.50, 0.03, 'Fuente: GBIF.org · Elaboración: @conmapas', fontsize=7,
        fontfamily='Segoe UI', color=GRAY_DIM, ha='center', alpha=0.3)

save_fig(fig, 'slide_08_checklist.png')

print("\n✅ All chart slides generated!")
