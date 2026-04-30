"""
Slide 1 — Portada/Hook v2 para carrusel @conmapas
"20 MILLONES de observaciones... ¿qué estamos contando realmente?"
"""
import matplotlib.pyplot as plt
import numpy as np
import os

# --- Config ---
SIZE = 1080
DPI = 150
BG = '#0d1117'
AMBER = '#fbbf24'
CYAN = '#22d3ee'
MAGENTA = '#e879f9'
WHITE = '#f1f5f9'
GRAY = '#94a3b8'
GRAY_DIM = '#475569'

fig, ax = plt.subplots(1, 1, figsize=(SIZE/DPI, SIZE/DPI), dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# --- Particle field ---
np.random.seed(42)
n_p = 600
x = np.random.uniform(0.02, 0.98, n_p)
y = np.random.uniform(0.02, 0.98, n_p)
r = np.sqrt((x - 0.5)**2 + (y - 0.5)**2)
alpha = np.clip(0.12 - r * 0.1, 0.01, 0.1)
sizes = np.random.uniform(0.3, 2.5, n_p)
colors = np.random.choice([CYAN, AMBER, MAGENTA], n_p, p=[0.55, 0.30, 0.15])
for i in range(n_p):
    ax.plot(x[i], y[i], 'o', color=colors[i], markersize=sizes[i], alpha=float(alpha[i]))

# --- Subtle glow circles ---
for cx, cy, rad, col in [(0.15, 0.75, 0.05, CYAN), (0.85, 0.70, 0.04, MAGENTA),
                          (0.78, 0.22, 0.035, AMBER), (0.22, 0.28, 0.03, CYAN)]:
    ax.add_patch(plt.Circle((cx, cy), rad, fill=True, facecolor=col, alpha=0.04))
    ax.add_patch(plt.Circle((cx, cy), rad, fill=False, edgecolor=col, linewidth=1, alpha=0.15))

# --- @conmapas top ---
ax.text(0.50, 0.93, '@conmapas', fontsize=13, fontfamily='Segoe UI',
        color=GRAY, ha='center', va='center', alpha=0.5, style='italic')

# --- Main number ---
ax.text(0.50, 0.64, '20', fontsize=130, fontweight='bold',
        fontfamily='Impact', color=AMBER, ha='center', va='center', alpha=0.95)
ax.text(0.50, 0.51, 'MILLONES', fontsize=50, fontweight='bold',
        fontfamily='Impact', color=WHITE, ha='center', va='center', alpha=0.95)

# --- Subtitle ---
ax.text(0.50, 0.435, 'de observaciones de animales', fontsize=17,
        fontfamily='Segoe UI', color=GRAY, ha='center', va='center')
ax.text(0.50, 0.395, 'registradas en Chile', fontsize=17,
        fontfamily='Segoe UI', color=GRAY, ha='center', va='center')

# --- Decorative line ---
ax.plot([0.28, 0.72], [0.365, 0.365], color=CYAN, linewidth=1.5, alpha=0.35)

# --- Hook question ---
ax.text(0.50, 0.30, '¿QUÉ ESTAMOS', fontsize=30, fontweight='bold',
        fontfamily='Impact', color=CYAN, ha='center', va='center', alpha=0.9)
ax.text(0.50, 0.255, 'CONTANDO REALMENTE?', fontsize=30, fontweight='bold',
        fontfamily='Impact', color=CYAN, ha='center', va='center', alpha=0.9)

# --- Swipe CTA ---
ax.text(0.50, 0.08, 'DESLIZA PARA DESCUBRIR  →', fontsize=11,
        fontfamily='Segoe UI', color=GRAY_DIM, ha='center', va='center', alpha=0.5)

# --- Source ---
ax.text(0.50, 0.03, 'Fuente: GBIF.org · Reino Animalia · Chile (CL)', fontsize=7,
        fontfamily='Segoe UI', color=GRAY_DIM, ha='center', va='center', alpha=0.3)

# --- Save ---
os.makedirs('slides', exist_ok=True)
plt.tight_layout(pad=0)
fig.savefig('slides/slide_01_hook.png', dpi=DPI, facecolor=BG, bbox_inches='tight', pad_inches=0)
plt.close()
print("Saved: slides/slide_01_hook.png")
