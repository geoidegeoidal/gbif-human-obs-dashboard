"""
Refactored chart slides for @conmapas carousel.
Exports each slide into its own folder with:
  - slide_XX_name.png       (full slide with dark background)
  - charts/chart_name.png   (chart-only, transparent background)

Uses matplotlib which IS the best library for static publication-quality
PNG exports with transparent background support.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json
import os

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


def make_dirs(slide_name):
    """Create slide folder and charts subfolder."""
    base = os.path.join('slides', slide_name)
    charts = os.path.join(base, 'charts')
    os.makedirs(charts, exist_ok=True)
    return base, charts


def save_slide(fig, base, name):
    """Save full slide (dark bg) and return path."""
    path = os.path.join(base, f'{name}.png')
    fig.savefig(path, dpi=DPI, facecolor=BG, bbox_inches='tight', pad_inches=0)
    print(f"  📄 {path}")
    return path


def save_chart(fig, charts_dir, name):
    """Save chart with transparent background."""
    path = os.path.join(charts_dir, f'{name}.png')
    fig.savefig(path, dpi=DPI, transparent=True, bbox_inches='tight', pad_inches=0.05)
    print(f"  🔲 {path} (transparent)")
    return path


# =================================================================
# SLIDE 1 — Hook
# =================================================================
print("\n━━━ Slide 01: Hook ━━━")
base, charts = make_dirs('slide_01_hook')

fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG), dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

np.random.seed(42)
n_p = 600
xp = np.random.uniform(0.02, 0.98, n_p)
yp = np.random.uniform(0.02, 0.98, n_p)
r = np.sqrt((xp - 0.5)**2 + (yp - 0.5)**2)
al = np.clip(0.12 - r * 0.1, 0.01, 0.1)
sz = np.random.uniform(0.3, 2.5, n_p)
co = np.random.choice([CYAN, AMBER, MAGENTA], n_p, p=[0.55, 0.30, 0.15])
for i in range(n_p):
    ax.plot(xp[i], yp[i], 'o', color=co[i], markersize=sz[i], alpha=float(al[i]))

for cx, cy, rad, col in [(0.15, 0.75, 0.05, CYAN), (0.85, 0.70, 0.04, MAGENTA),
                          (0.78, 0.22, 0.035, AMBER), (0.22, 0.28, 0.03, CYAN)]:
    ax.add_patch(plt.Circle((cx, cy), rad, fill=True, facecolor=col, alpha=0.04))
    ax.add_patch(plt.Circle((cx, cy), rad, fill=False, edgecolor=col, linewidth=1, alpha=0.15))

ax.text(0.50, 0.93, '@conmapas', fontsize=13, fontfamily='Segoe UI', color=GRAY, ha='center', alpha=0.5, style='italic')
ax.text(0.50, 0.64, '20', fontsize=130, fontweight='bold', fontfamily='Impact', color=AMBER, ha='center')
ax.text(0.50, 0.51, 'MILLONES', fontsize=50, fontweight='bold', fontfamily='Impact', color=WHITE, ha='center')
ax.text(0.50, 0.435, 'de observaciones de animales', fontsize=17, fontfamily='Segoe UI', color=GRAY, ha='center')
ax.text(0.50, 0.395, 'registradas en Chile', fontsize=17, fontfamily='Segoe UI', color=GRAY, ha='center')
ax.plot([0.28, 0.72], [0.365, 0.365], color=CYAN, linewidth=1.5, alpha=0.35)
ax.text(0.50, 0.30, '¿QUÉ ESTAMOS', fontsize=30, fontweight='bold', fontfamily='Impact', color=CYAN, ha='center', alpha=0.9)
ax.text(0.50, 0.255, 'CONTANDO REALMENTE?', fontsize=30, fontweight='bold', fontfamily='Impact', color=CYAN, ha='center', alpha=0.9)
ax.text(0.50, 0.08, 'DESLIZA PARA DESCUBRIR  →', fontsize=11, fontfamily='Segoe UI', color=GRAY_DIM, ha='center', alpha=0.5)
ax.text(0.50, 0.03, 'Fuente: GBIF.org · Reino Animalia · Chile (CL)', fontsize=7, fontfamily='Segoe UI', color=GRAY_DIM, ha='center', alpha=0.3)

plt.tight_layout(pad=0)
save_slide(fig, base, 'slide_01_hook')
save_chart(fig, charts, 'hook')
plt.close()


# =================================================================
# SLIDE 3 — Treemap Animalia
# =================================================================
print("\n━━━ Slide 03: Treemap ━━━")
base, charts = make_dirs('slide_03_treemap')

# --- Full slide ---
fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG), dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

ax.text(0.50, 0.95, '@conmapas', fontsize=10, fontfamily='Segoe UI', color=GRAY, ha='center', alpha=0.4, style='italic')
ax.text(0.50, 0.88, 'ANIMALIA ≠', fontsize=38, fontweight='bold', fontfamily='Impact', color=AMBER, ha='center')
ax.text(0.50, 0.82, 'SOLO LOS ANIMALES QUE IMAGINAS', fontsize=22, fontweight='bold', fontfamily='Impact', color=WHITE, ha='center')
ax.text(0.50, 0.76, 'El Taxonomic Backbone de GBIF incluye desde ballenas hasta tardígrados', fontsize=10, fontfamily='Segoe UI', color=GRAY, ha='center', alpha=0.6)

blocks = [
    ('Chordata\n82.6%', CYAN, 0.08, 0.28, 0.55, 0.45),
    ('Arthropoda\n14.8%', AMBER, 0.08, 0.18, 0.55, 0.09),
    ('Mollusca\n1.5%', MAGENTA, 0.65, 0.55, 0.30, 0.18),
    ('Otros\n23 phyla', GRAY_DIM, 0.65, 0.28, 0.30, 0.25),
]
for label, color, x, y, w, h in blocks:
    rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01", facecolor=color, alpha=0.25, edgecolor=color, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, fontsize=14, fontweight='bold', fontfamily='Segoe UI', color=WHITE, ha='center', va='center')

ax.add_patch(mpatches.FancyBboxPatch((0.06, 0.06), 0.88, 0.09, boxstyle="round,pad=0.01", facecolor=RED, alpha=0.1, edgecolor=RED, linewidth=1))
ax.text(0.50, 0.105, '40.3% de registros sin Class asignada (8.3M)', fontsize=12, fontfamily='Segoe UI', color=RED, ha='center', fontweight='bold')

plt.tight_layout(pad=0)
save_slide(fig, base, 'slide_03_treemap')
plt.close()

# --- Chart only (transparent) ---
fig, ax = plt.subplots(1, 1, figsize=(FIG * 0.9, FIG * 0.5), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

for label, color, x, y, w, h in [
    ('Chordata\n82.6%', CYAN, 0.02, 0.25, 0.60, 0.70),
    ('Arthropoda\n14.8%', AMBER, 0.02, 0.05, 0.60, 0.18),
    ('Mollusca\n1.5%', MAGENTA, 0.65, 0.60, 0.33, 0.35),
    ('Otros 23 phyla', GRAY_DIM, 0.65, 0.05, 0.33, 0.52),
]:
    rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01", facecolor=color, alpha=0.3, edgecolor=color, linewidth=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, fontsize=16, fontweight='bold', fontfamily='Segoe UI', color=WHITE, ha='center', va='center')

save_chart(fig, charts, 'treemap_phylum')
plt.close()


# =================================================================
# SLIDE 4 — Timeline
# =================================================================
print("\n━━━ Slide 04: Timeline ━━━")
base, charts = make_dirs('slide_04_timeline')

years_data = eda['year_dist']
years = [d['year'] for d in years_data]
counts = [d['n'] for d in years_data]

# --- Full slide ---
fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG), dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.fill_between(years, counts, alpha=0.3, color=CYAN)
ax.plot(years, counts, color=CYAN, linewidth=2, alpha=0.9)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(GRAY_DIM); ax.spines['bottom'].set_color(GRAY_DIM)
ax.tick_params(colors=GRAY, labelsize=8)
ax.yaxis.set_major_formatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K')
ax.set_xlim(1970, 2025); ax.set_ylim(0, max(counts) * 1.15)

ax.annotate('eBird +\niNaturalist', xy=(2010, 801414), xytext=(1985, 1500000),
            fontsize=10, fontfamily='Segoe UI', color=AMBER, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=AMBER, lw=1.5), ha='center')
peak_year = years[np.argmax(counts)]
peak_val = max(counts)
ax.annotate(f'{peak_val/1e6:.1f}M', xy=(peak_year, peak_val),
            xytext=(peak_year - 5, peak_val + 100000),
            fontsize=9, fontfamily='Segoe UI', color=CYAN, fontweight='bold', ha='center')

ax.text(0.5, 0.97, 'DE 5.000 A 1.8 MILLONES', fontsize=28, fontweight='bold', fontfamily='Impact', color=WHITE, ha='center', va='top', transform=ax.transAxes)
ax.text(0.5, 0.89, 'DE REGISTROS POR AÑO', fontsize=22, fontweight='bold', fontfamily='Impact', color=GRAY, ha='center', va='top', transform=ax.transAxes)
ax.text(0.5, 0.05, '2020–2024 = 7.8M registros (38% del total)', fontsize=9, fontfamily='Segoe UI', color=GRAY, ha='center', transform=ax.transAxes, alpha=0.6)
ax.text(0.01, 0.01, '@conmapas', fontsize=8, fontfamily='Segoe UI', color=GRAY_DIM, transform=ax.transAxes, alpha=0.4, style='italic')

plt.tight_layout(pad=0.8)
save_slide(fig, base, 'slide_04_timeline')
plt.close()

# --- Chart only (transparent) ---
fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG * 0.55), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.fill_between(years, counts, alpha=0.3, color=CYAN)
ax.plot(years, counts, color=CYAN, linewidth=2.5, alpha=0.9)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(WHITE); ax.spines['bottom'].set_color(WHITE)
ax.spines['left'].set_alpha(0.3); ax.spines['bottom'].set_alpha(0.3)
ax.tick_params(colors=WHITE, labelsize=9)
ax.yaxis.set_major_formatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K')
ax.set_xlim(1970, 2025); ax.set_ylim(0, max(counts) * 1.1)

ax.annotate('eBird +\niNaturalist', xy=(2010, 801414), xytext=(1985, 1500000),
            fontsize=11, fontfamily='Segoe UI', color=AMBER, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=AMBER, lw=2), ha='center')

plt.tight_layout(pad=0.5)
save_chart(fig, charts, 'timeline_area')
plt.close()


# =================================================================
# SLIDE 5 — Sesgo Ciencia Ciudadana
# =================================================================
print("\n━━━ Slide 05: Sesgo ━━━")
base, charts = make_dirs('slide_05_sesgo')

fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG), dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

ax.text(0.50, 0.95, '@conmapas', fontsize=10, fontfamily='Segoe UI', color=GRAY, ha='center', alpha=0.4, style='italic')
ax.text(0.50, 0.88, '9 DE CADA 10 REGISTROS', fontsize=30, fontweight='bold', fontfamily='Impact', color=WHITE, ha='center')
ax.text(0.50, 0.82, 'SON OBSERVACIONES HUMANAS', fontsize=24, fontweight='bold', fontfamily='Impact', color=CYAN, ha='center')

basis_data = [('HUMAN_OBSERVATION', 18662018, CYAN), ('MACHINE_OBSERVATION', 1618695, AMBER), ('PRESERVED_SPECIMEN', 424615, MAGENTA), ('Otros', 95785, GRAY_DIM)]
total_b = sum(b[1] for b in basis_data)
y_pos = 0.72
for label, n, color in basis_data:
    width = (n / total_b) * 0.80
    rect = mpatches.FancyBboxPatch((0.08, y_pos), width, 0.04, boxstyle="round,pad=0.005", facecolor=color, alpha=0.6, edgecolor=color, linewidth=0.5)
    ax.add_patch(rect)
    pct = n / total_b * 100
    ax.text(0.08 + width + 0.02, y_pos + 0.02, f'{pct:.1f}%', fontsize=9, fontfamily='Segoe UI', color=color, va='center', fontweight='bold')
    ax.text(0.06, y_pos + 0.02, label.replace('_', ' ').title(), fontsize=8, fontfamily='Segoe UI', color=GRAY, va='center', ha='right')
    y_pos -= 0.065

ax.plot([0.08, 0.92], [0.50, 0.50], color=GRAY_DIM, linewidth=0.5, alpha=0.3)
ax.text(0.50, 0.46, 'EN OBSERVACIÓN HUMANA:', fontsize=14, fontweight='bold', fontfamily='Impact', color=WHITE, ha='center')

ax.add_patch(mpatches.FancyBboxPatch((0.08, 0.38), 0.80, 0.04, boxstyle="round,pad=0.005", facecolor=CYAN, alpha=0.5, edgecolor=CYAN, linewidth=0.5))
ax.text(0.10, 0.40, 'Aves: 7.7M (41%)', fontsize=11, fontfamily='Segoe UI', color=WHITE, va='center', fontweight='bold')

ax.add_patch(mpatches.FancyBboxPatch((0.08, 0.31), 0.80 * (66624/7701624), 0.04, boxstyle="round,pad=0.005", facecolor=GREEN, alpha=0.5, edgecolor=GREEN, linewidth=0.5))
ax.text(0.10, 0.33, 'Insecta: 67K (0.4%)', fontsize=11, fontfamily='Segoe UI', color=GREEN, va='center', fontweight='bold')

ax.add_patch(mpatches.FancyBboxPatch((0.06, 0.16), 0.88, 0.10, boxstyle="round,pad=0.01", facecolor=AMBER, alpha=0.08, edgecolor=AMBER, linewidth=1))
ax.text(0.50, 0.23, 'Pero en museos: Insecta = 249K especímenes', fontsize=11, fontfamily='Segoe UI', color=AMBER, ha='center', fontweight='bold')
ax.text(0.50, 0.19, '"Los insectos se conocen por museos, no por ciencia ciudadana"', fontsize=9, fontfamily='Segoe UI', color=GRAY, ha='center', style='italic')
ax.text(0.50, 0.04, 'Fuente: GBIF.org · Reino Animalia · Chile', fontsize=7, fontfamily='Segoe UI', color=GRAY_DIM, ha='center', alpha=0.3)

plt.tight_layout(pad=0)
save_slide(fig, base, 'slide_05_sesgo')
plt.close()

# --- Chart: basis of record bars (transparent) ---
fig, ax = plt.subplots(1, 1, figsize=(FIG * 0.9, FIG * 0.35), dpi=DPI)
fig.patch.set_alpha(0); ax.set_facecolor('none')

labels = ['Human Obs.', 'Machine Obs.', 'Pres. Specimen', 'Otros']
values = [18662018, 1618695, 424615, 95785]
colors_b = [CYAN, AMBER, MAGENTA, GRAY_DIM]
bars = ax.barh(labels, values, color=colors_b, alpha=0.7, edgecolor=colors_b, linewidth=0.5, height=0.6)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(WHITE); ax.spines['bottom'].set_color(WHITE)
ax.spines['left'].set_alpha(0.3); ax.spines['bottom'].set_alpha(0.3)
ax.tick_params(colors=WHITE, labelsize=10)
ax.xaxis.set_major_formatter(lambda x, p: f'{x/1e6:.0f}M')
ax.invert_yaxis()
for bar, val in zip(bars, values):
    ax.text(bar.get_width() + 200000, bar.get_y() + bar.get_height()/2, f'{val/1e6:.1f}M', color=WHITE, va='center', fontsize=9, fontfamily='Segoe UI')

plt.tight_layout(pad=0.3)
save_chart(fig, charts, 'basis_of_record_bars')
plt.close()

# --- Chart: Aves vs Insecta comparison (transparent) ---
fig, ax = plt.subplots(1, 1, figsize=(FIG * 0.9, FIG * 0.25), dpi=DPI)
fig.patch.set_alpha(0); ax.set_facecolor('none')

ax.barh(['Insecta (Human Obs)', 'Aves (Human Obs)'], [66624, 7701624], color=[GREEN, CYAN], alpha=0.7, height=0.5)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(WHITE); ax.spines['bottom'].set_color(WHITE)
ax.spines['left'].set_alpha(0.3); ax.spines['bottom'].set_alpha(0.3)
ax.tick_params(colors=WHITE, labelsize=10)
ax.xaxis.set_major_formatter(lambda x, p: f'{x/1e6:.1f}M')

plt.tight_layout(pad=0.3)
save_chart(fig, charts, 'aves_vs_insecta')
plt.close()


# =================================================================
# SLIDE 6 — ABSENT + Fósiles
# =================================================================
print("\n━━━ Slide 06: ABSENT + Fósiles ━━━")
base, charts = make_dirs('slide_06_absent_fossil')

fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG), dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

ax.text(0.50, 0.95, '@conmapas', fontsize=10, fontfamily='Segoe UI', color=GRAY, ha='center', alpha=0.4, style='italic')
ax.text(0.50, 0.88, '1.17 MILLONES', fontsize=42, fontweight='bold', fontfamily='Impact', color=RED, ha='center')
ax.text(0.50, 0.81, 'DE REGISTROS DICEN "AUSENTE"', fontsize=24, fontweight='bold', fontfamily='Impact', color=WHITE, ha='center')

ax.add_patch(mpatches.FancyBboxPatch((0.06, 0.55), 0.88, 0.20, boxstyle="round,pad=0.015", facecolor=RED, alpha=0.08, edgecolor=RED, linewidth=1.5))
ax.text(0.50, 0.72, 'occurrenceStatus = ABSENT', fontsize=16, fontweight='bold', fontfamily='Segoe UI', color=RED, ha='center')
ax.text(0.50, 0.66, '1,170,113 registros (5.6%)', fontsize=14, fontfamily='Segoe UI', color=WHITE, ha='center')
ax.text(0.50, 0.60, '"Fuimos, buscamos, y NO encontramos el animal"', fontsize=10, fontfamily='Segoe UI', color=GRAY, ha='center', style='italic')
ax.text(0.50, 0.57, 'Si no filtras, lo cuentas erróneamente como presencia', fontsize=9, fontfamily='Segoe UI', color=GRAY, ha='center', alpha=0.7)

ax.add_patch(mpatches.FancyBboxPatch((0.06, 0.26), 0.88, 0.22, boxstyle="round,pad=0.015", facecolor=AMBER, alpha=0.08, edgecolor=AMBER, linewidth=1.5))
ax.text(0.50, 0.44, 'basisOfRecord = FOSSIL_SPECIMEN', fontsize=16, fontweight='bold', fontfamily='Segoe UI', color=AMBER, ha='center')
ax.text(0.50, 0.38, '7,379 registros', fontsize=14, fontfamily='Segoe UI', color=WHITE, ha='center')
ax.text(0.50, 0.34, 'Incertidumbre promedio: 1,949 km', fontsize=12, fontfamily='Segoe UI', color=AMBER, ha='center', fontweight='bold')
ax.text(0.50, 0.30, '"Moluscos del Mesozoico aparecen como puntos', fontsize=9, fontfamily='Segoe UI', color=GRAY, ha='center', style='italic')
ax.text(0.50, 0.275, 'en el Desierto de Atacama actual"', fontsize=9, fontfamily='Segoe UI', color=GRAY, ha='center', style='italic')

ax.text(0.50, 0.08, 'Si haces un SDM o análisis de biodiversidad actual,', fontsize=10, fontfamily='Segoe UI', color=WHITE, ha='center')
ax.text(0.50, 0.05, 'estos registros generan ruido geoespacial absurdo', fontsize=10, fontfamily='Segoe UI', color=RED, ha='center', fontweight='bold')

plt.tight_layout(pad=0)
save_slide(fig, base, 'slide_06_absent_fossil')
save_chart(fig, charts, 'absent_fossil_info')
plt.close()


# =================================================================
# SLIDE 7 — Incertidumbre
# =================================================================
print("\n━━━ Slide 07: Incertidumbre ━━━")
base, charts = make_dirs('slide_07_incertidumbre')

unc = meth['coord_uncertainty']
categories = ['Sin dato', '≤ 10m', '10-100m', '100m-1km', '1-10km', '10-100km', '>100km']
values = [unc['sin_incertidumbre'], unc['hasta_10m'], unc['10_100m'],
          unc['100_1000m'], unc['1_10km'], unc['10_100km'], unc['mas_100km']]
colors_bar = [RED, GREEN, GREEN, CYAN, AMBER, MAGENTA, RED]

# --- Full slide ---
fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG), dpi=DPI)
fig.patch.set_facecolor(BG); ax.set_facecolor(BG)

max_val = max(values)
bar_w = [v / max_val for v in values]
y_pos = np.arange(len(categories))

ax.barh(y_pos, bar_w, height=0.6, color=colors_bar, alpha=0.6, edgecolor=colors_bar, linewidth=0.5)
for i, (cat, val) in enumerate(zip(categories, values)):
    pct = val / unc['total'] * 100
    ax.text(-0.02, i, cat, fontsize=9, fontfamily='Segoe UI', color=GRAY, ha='right', va='center')
    label = f'{pct:.1f}%  ({val/1e6:.1f}M)' if pct >= 1 else f'{pct:.1f}%  ({val:,.0f})'
    ax.text(bar_w[i] + 0.02, i, label, fontsize=8, fontfamily='Segoe UI', color=WHITE, ha='left', va='center')

ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False); ax.spines['bottom'].set_visible(False)
ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
ax.set_xlim(-0.35, 1.4); ax.invert_yaxis()

ax.text(0.5, 1.08, '95% DE LOS REGISTROS', fontsize=28, fontweight='bold', fontfamily='Impact', color=RED, ha='center', transform=ax.transAxes)
ax.text(0.5, 1.01, 'NO REPORTAN SU PRECISIÓN', fontsize=24, fontweight='bold', fontfamily='Impact', color=WHITE, ha='center', transform=ax.transAxes)
ax.text(0.5, -0.08, f'Mediana: 1 km · Máximo: 7,945 km · Promedio: 6.5 km', fontsize=9, fontfamily='Segoe UI', color=GRAY, ha='center', transform=ax.transAxes)
ax.text(0.01, -0.13, '@conmapas', fontsize=8, fontfamily='Segoe UI', color=GRAY_DIM, transform=ax.transAxes, alpha=0.4, style='italic')

plt.tight_layout(pad=1.2)
save_slide(fig, base, 'slide_07_incertidumbre')
plt.close()

# --- Chart only (transparent) ---
fig, ax = plt.subplots(1, 1, figsize=(FIG * 0.85, FIG * 0.5), dpi=DPI)
fig.patch.set_alpha(0); ax.set_facecolor('none')

ax.barh(y_pos, bar_w, height=0.6, color=colors_bar, alpha=0.7, edgecolor=colors_bar, linewidth=0.5)
for i, (cat, val) in enumerate(zip(categories, values)):
    pct = val / unc['total'] * 100
    ax.text(-0.02, i, cat, fontsize=10, fontfamily='Segoe UI', color=WHITE, ha='right', va='center')
    label = f'{pct:.1f}%' if pct >= 0.1 else f'{pct:.2f}%'
    ax.text(bar_w[i] + 0.02, i, label, fontsize=9, fontfamily='Segoe UI', color=WHITE, ha='left', va='center', fontweight='bold')

ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False); ax.spines['bottom'].set_visible(False)
ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
ax.set_xlim(-0.35, 1.3); ax.invert_yaxis()

plt.tight_layout(pad=0.3)
save_chart(fig, charts, 'uncertainty_bars')
plt.close()


# =================================================================
# SLIDE 8 — Checklist
# =================================================================
print("\n━━━ Slide 08: Checklist ━━━")
base, charts = make_dirs('slide_08_checklist')

fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG), dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

ax.text(0.50, 0.95, '@conmapas', fontsize=10, fontfamily='Segoe UI', color=GRAY, ha='center', alpha=0.4, style='italic')
ax.text(0.50, 0.87, 'ANTES DE MAPEAR', fontsize=38, fontweight='bold', fontfamily='Impact', color=CYAN, ha='center')
ax.text(0.50, 0.80, 'FILTRA', fontsize=50, fontweight='bold', fontfamily='Impact', color=AMBER, ha='center')

items = [
    ('Filtrar occurrenceStatus = PRESENT', GREEN),
    ('Excluir FOSSIL_SPECIMEN', GREEN),
    ('Revisar coordinateUncertaintyInMeters', GREEN),
    ('Separar por basisOfRecord según tu pregunta', GREEN),
    ('Animalia incluye 27+ phyla, no solo vertebrados', AMBER),
]
y_start = 0.67
for i, (text, accent) in enumerate(items):
    y = y_start - i * 0.09
    ax.add_patch(mpatches.FancyBboxPatch((0.06, y - 0.025), 0.88, 0.06, boxstyle="round,pad=0.008", facecolor=accent, alpha=0.06, edgecolor=accent, linewidth=0.8))
    marker = '>>>' if accent == AMBER else '  ✓'
    ax.text(0.10, y + 0.005, marker, fontsize=12, fontfamily='Segoe UI', color=accent, ha='center', va='center', fontweight='bold')
    ax.text(0.15, y + 0.005, text, fontsize=11, fontfamily='Segoe UI', color=WHITE, va='center')

ax.plot([0.15, 0.85], [0.18, 0.18], color=CYAN, linewidth=1, alpha=0.3)
ax.text(0.50, 0.13, '"Un dato sin contexto', fontsize=16, fontweight='bold', fontfamily='Segoe UI', color=WHITE, ha='center')
ax.text(0.50, 0.09, 'es un mapa que miente"', fontsize=16, fontweight='bold', fontfamily='Segoe UI', color=CYAN, ha='center')
ax.text(0.50, 0.03, 'Fuente: GBIF.org · Elaboración: @conmapas', fontsize=7, fontfamily='Segoe UI', color=GRAY_DIM, ha='center', alpha=0.3)

plt.tight_layout(pad=0)
save_slide(fig, base, 'slide_08_checklist')
save_chart(fig, charts, 'checklist')
plt.close()


print("\n✅ All chart slides exported!")
print("   Each slide folder contains:")
print("   - Full slide PNG (dark background)")
print("   - charts/ subfolder with transparent PNGs")
