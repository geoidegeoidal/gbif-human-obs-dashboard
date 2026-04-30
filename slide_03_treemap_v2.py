"""
Slide 3 — ¿Qué es Animalia? (Horizontal bar chart)
Shows phylum distribution clearly despite extreme proportions.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json
import os

with open('eda_results.json', 'r', encoding='utf-8') as f:
    eda = json.load(f)

SIZE, DPI = 1080, 150
FIG = SIZE / DPI
BG = '#0d1117'
AMBER = '#fbbf24'
CYAN = '#22d3ee'
MAGENTA = '#e879f9'
GREEN = '#4ade80'
RED = '#f87171'
ORANGE = '#fb923c'
TEAL = '#2dd4bf'
VIOLET = '#a78bfa'
ROSE = '#fb7185'
WHITE = '#f1f5f9'
GRAY = '#94a3b8'
GRAY_DIM = '#475569'

base = os.path.join('slides', 'slide_03_treemap')
charts_dir = os.path.join(base, 'charts')
os.makedirs(charts_dir, exist_ok=True)

# Data
phyla = eda['phylum_top15']
total = sum(p['n'] for p in phyla)

# Top phyla for display
display = [
    ('Chordata', 17185471, CYAN),
    ('Arthropoda', 3078001, AMBER),
    ('Mollusca', 309374, MAGENTA),
    ('Echinodermata', 83034, GREEN),
    ('Cnidaria', 60764, ORANGE),
    ('Annelida', 30230, TEAL),
    ('Porifera', 17196, VIOLET),
    ('Bryozoa', 9003, ROSE),
]

labels = [d[0] for d in display]
values = [d[1] for d in display]
colors = [d[2] for d in display]
pcts = [v / total * 100 for v in values]

# Remaining
shown_total = sum(values)
remaining = total - shown_total
remaining_phyla = 19  # 27 total - 8 shown = 19


# ================================================================
# Full slide
# ================================================================
fig, ax = plt.subplots(1, 1, figsize=(FIG, FIG), dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Title
ax.text(0.50, 0.96, '@conmapas', fontsize=10, fontfamily='Segoe UI',
        color=GRAY, ha='center', alpha=0.4, style='italic')
ax.text(0.50, 0.90, 'ANIMALIA ≠', fontsize=40, fontweight='bold',
        fontfamily='Impact', color=AMBER, ha='center')
ax.text(0.50, 0.84, 'SOLO LOS ANIMALES QUE IMAGINAS', fontsize=20,
        fontweight='bold', fontfamily='Impact', color=WHITE, ha='center')

# Bars
bar_left = 0.30
bar_max_width = 0.58
bar_height = 0.038
y_start = 0.76
spacing = 0.055

for i, (label, val, color, pct) in enumerate(zip(labels, values, colors, pcts)):
    y = y_start - i * spacing

    # Bar width (use log-ish scale to make smaller bars visible)
    # Primary bar proportional, but with a min width
    width = max((val / values[0]) * bar_max_width, 0.015)

    # Bar
    rect = mpatches.FancyBboxPatch(
        (bar_left, y - bar_height/2), width, bar_height,
        boxstyle="round,pad=0.004",
        facecolor=color, alpha=0.6, edgecolor=color, linewidth=0.8
    )
    ax.add_patch(rect)

    # Label left
    ax.text(bar_left - 0.02, y, label, fontsize=10, fontfamily='Segoe UI',
            color=WHITE, ha='right', va='center', fontweight='bold')

    # Value right
    if pct >= 1:
        val_text = f'{pct:.1f}% ({val/1e6:.1f}M)'
    elif pct >= 0.1:
        val_text = f'{pct:.1f}% ({val:,.0f})'
    else:
        val_text = f'{pct:.2f}% ({val:,.0f})'

    ax.text(bar_left + width + 0.02, y, val_text, fontsize=8.5,
            fontfamily='Segoe UI', color=color, va='center', fontweight='bold')

# Remaining phyla note
y_remaining = y_start - len(display) * spacing - 0.01
ax.text(bar_left, y_remaining, f'+ {remaining_phyla} phyla más ({remaining:,.0f} registros)',
        fontsize=9, fontfamily='Segoe UI', color=GRAY, va='center')
ax.text(bar_left, y_remaining - 0.03,
        'Tardigrada · Rotifera · Nematoda · Platyhelminthes · Sipuncula...',
        fontsize=7.5, fontfamily='Segoe UI', color=GRAY_DIM, va='center', style='italic')

# Separator
ax.plot([0.06, 0.94], [y_remaining - 0.06, y_remaining - 0.06],
        color=GRAY_DIM, linewidth=0.5, alpha=0.3)

# Warning box
warn_y = y_remaining - 0.10
ax.add_patch(mpatches.FancyBboxPatch(
    (0.06, warn_y - 0.04), 0.88, 0.065, boxstyle="round,pad=0.01",
    facecolor=RED, alpha=0.08, edgecolor=RED, linewidth=1
))
ax.text(0.50, warn_y - 0.005,
        '40.3% de registros sin Class asignada (8.3M)',
        fontsize=11, fontfamily='Segoe UI', color=RED, ha='center',
        va='center', fontweight='bold')

# Source
ax.text(0.50, 0.03, 'Fuente: GBIF.org · Distribución por Phylum · Chile',
        fontsize=7, fontfamily='Segoe UI', color=GRAY_DIM, ha='center', alpha=0.3)

plt.tight_layout(pad=0)
fig.savefig(os.path.join(base, 'slide_03_treemap.png'), dpi=DPI, facecolor=BG,
            bbox_inches='tight', pad_inches=0)
print(f"  Saved full slide")
plt.close()


# ================================================================
# Transparent chart only (just the bars)
# ================================================================
fig, ax = plt.subplots(1, 1, figsize=(FIG * 0.9, FIG * 0.55), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

y_pos = np.arange(len(display))[::-1]
bar_vals = [v / 1e6 for v in values]  # in millions

bars = ax.barh(y_pos, bar_vals, height=0.6, color=colors, alpha=0.7,
               edgecolor=colors, linewidth=0.5)

ax.set_yticks(y_pos)
ax.set_yticklabels(labels)
ax.tick_params(colors=WHITE, labelsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(WHITE)
ax.spines['bottom'].set_color(WHITE)
ax.spines['left'].set_alpha(0.3)
ax.spines['bottom'].set_alpha(0.3)
ax.xaxis.set_major_formatter(lambda x, p: f'{x:.0f}M' if x >= 1 else f'{x*1000:.0f}K')

for bar, pct, color in zip(bars, pcts, colors):
    ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2,
            f'{pct:.1f}%', color=color, va='center', fontsize=9,
            fontfamily='Segoe UI', fontweight='bold')

plt.tight_layout(pad=0.3)
fig.savefig(os.path.join(charts_dir, 'phylum_bars.png'), dpi=DPI,
            transparent=True, bbox_inches='tight', pad_inches=0.05)
print(f"  Saved transparent chart")
plt.close()

print("\n✅ Slide 3 rebuilt as horizontal bar chart!")
