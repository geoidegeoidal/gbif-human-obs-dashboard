"""
Slide 1 — Portada/Hook para carrusel @conmapas
Estilo: fondo oscuro, tipografía bold, colores neón
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np

# --- Config ---
SIZE = 1080
DPI = 150
BG_COLOR = '#0d1117'       # GitHub dark
ACCENT_CYAN = '#22d3ee'    # cyan vibrante
ACCENT_AMBER = '#fbbf24'   # amber cálido
ACCENT_MAGENTA = '#e879f9' # magenta
TEXT_WHITE = '#f1f5f9'
TEXT_GRAY = '#94a3b8'

fig, ax = plt.subplots(1, 1, figsize=(SIZE/DPI, SIZE/DPI), dpi=DPI)
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# --- Partículas de fondo (simula puntos de ocurrencia dispersos) ---
np.random.seed(42)
n_particles = 800
x_p = np.random.uniform(0.05, 0.95, n_particles)
y_p = np.random.uniform(0.05, 0.95, n_particles)
# Concentración mayor en el centro
r = np.sqrt((x_p - 0.5)**2 + (y_p - 0.5)**2)
alpha_p = np.clip(0.15 - r * 0.15, 0.02, 0.12)
sizes = np.random.uniform(0.5, 3, n_particles)
colors_p = np.random.choice([ACCENT_CYAN, ACCENT_AMBER, ACCENT_MAGENTA], n_particles, p=[0.6, 0.3, 0.1])
for i in range(n_particles):
    ax.plot(x_p[i], y_p[i], 'o', color=colors_p[i], markersize=sizes[i], alpha=float(alpha_p[i]))

# --- Anillos decorativos (glow circles) ---
for i, (cx, cy, rad, col) in enumerate([
    (0.18, 0.72, 0.06, ACCENT_CYAN),
    (0.82, 0.68, 0.05, ACCENT_MAGENTA),
    (0.75, 0.25, 0.04, ACCENT_AMBER),
    (0.25, 0.30, 0.035, ACCENT_CYAN),
]):
    circle = plt.Circle((cx, cy), rad, fill=False, edgecolor=col, linewidth=1.5, alpha=0.25)
    ax.add_patch(circle)
    circle2 = plt.Circle((cx, cy), rad * 0.6, fill=True, facecolor=col, alpha=0.05)
    ax.add_patch(circle2)

# --- Siluetas animales con emojis/texto ---
animals = [
    ('🐋', 0.15, 0.78, 28, 0.6),
    ('🦅', 0.85, 0.75, 30, 0.7),
    ('🦎', 0.80, 0.22, 24, 0.5),
    ('🦀', 0.20, 0.25, 24, 0.5),
    ('🐟', 0.50, 0.15, 22, 0.4),
    ('🦋', 0.12, 0.50, 20, 0.4),
    ('🐙', 0.88, 0.48, 22, 0.4),
]
for emoji, ex, ey, es, ea in animals:
    ax.text(ex, ey, emoji, fontsize=es, ha='center', va='center', alpha=ea,
            fontfamily='Segoe UI Emoji')

# --- Texto principal ---
# Número hero
ax.text(0.50, 0.62, '20', fontsize=120, fontweight='bold',
        fontfamily='Impact', color=ACCENT_AMBER, ha='center', va='center',
        alpha=0.95)
ax.text(0.50, 0.50, 'MILLONES', fontsize=48, fontweight='bold',
        fontfamily='Impact', color=TEXT_WHITE, ha='center', va='center',
        alpha=0.95)

# Subtítulo
ax.text(0.50, 0.43, 'de observaciones de animales', fontsize=18,
        fontfamily='Segoe UI', color=TEXT_GRAY, ha='center', va='center')
ax.text(0.50, 0.385, 'registradas en Chile', fontsize=18,
        fontfamily='Segoe UI', color=TEXT_GRAY, ha='center', va='center')

# Línea decorativa
ax.plot([0.30, 0.70], [0.36, 0.36], color=ACCENT_CYAN, linewidth=1.5, alpha=0.4)

# Pregunta hook
ax.text(0.50, 0.30, '¿DÓNDE ESTÁN?', fontsize=32, fontweight='bold',
        fontfamily='Impact', color=ACCENT_CYAN, ha='center', va='center',
        alpha=0.9)

# Instrucción deslizar
ax.text(0.50, 0.08, 'DESLIZA PARA VER  →', fontsize=12,
        fontfamily='Segoe UI', color=TEXT_GRAY, ha='center', va='center',
        alpha=0.5)

# Logo / branding
ax.text(0.50, 0.93, '@conmapas', fontsize=14,
        fontfamily='Segoe UI', color=TEXT_GRAY, ha='center', va='center',
        alpha=0.6, style='italic')

# Fuente de datos
ax.text(0.50, 0.03, 'Fuente: GBIF.org · Reino Animalia · Chile', fontsize=8,
        fontfamily='Segoe UI', color=TEXT_GRAY, ha='center', va='center',
        alpha=0.35)

# --- Guardar ---
plt.tight_layout(pad=0)
output_path = 'slides/slide_01_portada.png'
import os
os.makedirs('slides', exist_ok=True)
fig.savefig(output_path, dpi=DPI, facecolor=BG_COLOR, bbox_inches='tight', pad_inches=0)
plt.close()
print(f"Saved: {output_path}")
