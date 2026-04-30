"""
Genera un PDF con la propuesta completa del carrusel @conmapas.
Cada página muestra la imagen del slide + descripción narrativa.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import numpy as np
import os

BG = '#0d1117'
WHITE = '#f1f5f9'
GRAY = '#94a3b8'
GRAY_DIM = '#475569'
CYAN = '#22d3ee'
AMBER = '#fbbf24'
RED = '#f87171'

DPI = 150
W, H = 11, 8.5  # Letter landscape

slides_info = [
    {
        'title': 'PROPUESTA CARRUSEL @conmapas',
        'subtitle': '20 millones de animales... ¿o no?',
        'image': None,
        'desc': [
            'Concepto:  Narrativa de datos con rigor metodológico.',
            'Fuente:  GBIF.org · Reino Animalia · Chile · 20.8M registros.',
            '',
            'Estructura en 3 actos:',
            '',
            '  ACT 1 — EL IMPACTO',
            '    Slide 1: Hook (20 millones ¿qué contamos?)',
            '    Slide 2: Mapa crudo (todos los datos sin filtrar)',
            '',
            '  ACT 2 — DESMONTANDO LOS SESGOS',
            '    Slide 3: ¿Qué es Animalia? (distribución por Phylum)',
            '    Slide 4: Timeline (explosión post-2010)',
            '    Slide 5: Sesgo ciencia ciudadana (9/10 human obs)',
            '    Slide 6: Datos a excluir (1.17M ABSENT + fósiles)',
            '    Slide 7: Incertidumbre (95% sin dato de precisión)',
            '',
            '  ACT 3 — LOS DATOS LIMPIOS',
            '    Slide 8:  Checklist metodológico',
            '    Slide 9:  Mapa filtrado por Phylum (QGIS)',
            '    Slide 10: Mapa filtrado por Class (QGIS)',
            '    Slide 11: Mapa filtrado por basisOfRecord (QGIS)',
            '',
            'Paleta:  Fondo #0d1117 · Cyan #22d3ee · Amber #fbbf24 · Magenta #e879f9',
            'Formato: 1080 × 1080 px cuadrado · Mapas a cargo del usuario en QGIS',
        ]
    },
    {
        'title': 'SLIDE 1 — HOOK',
        'subtitle': '20 millones de observaciones... ¿qué estamos contando realmente?',
        'image': 'slides/slide_01_hook/slide_01_hook.png',
        'desc': [
            'Objetivo: Generar curiosidad metodológica.',
            '',
            'Elementos:',
            '  • Número "20 MILLONES" en amber (impacto visual)',
            '  • Pregunta provocadora: "¿Qué estamos contando realmente?"',
            '  • Partículas decorativas de fondo',
            '  • CTA: "Desliza para descubrir"',
            '',
            'Tono: Enganchar sin revelar la respuesta.',
        ]
    },
    {
        'title': 'SLIDE 2 — MAPA CRUDO',
        'subtitle': 'Así se ven 20.8M registros sin filtrar',
        'image': None,
        'desc': [
            'Objetivo: Mostrar TODOS los datos crudos como punto de partida.',
            '',
            'Este mapa se hará en QGIS con:',
            '  • GeoParquet: geoparquet/slide_02_raw_all.parquet',
            '  • 20,636,696 puntos en EPSG:3857',
            '  • Color único (cyan sobre fondo oscuro)',
            '  • Sin filtrar: incluye ABSENT, fósiles, todo',
            '',
            'Mensaje: "Este mapa esconde varios problemas..."',
            'Se re-contextualizará con los mapas filtrados del final.',
        ]
    },
    {
        'title': 'SLIDE 3 — ¿QUÉ ES ANIMALIA?',
        'subtitle': 'Distribución por Phylum',
        'image': 'slides/slide_03_treemap/slide_03_treemap.png',
        'desc': [
            'Objetivo: Revelar que "Animalia" es mucho más que vertebrados.',
            '',
            'Datos clave:',
            '  • Chordata: 82.6% (17.2M) — domina por eBird',
            '  • Arthropoda: 14.8% (3.1M) — incluye Malacostraca',
            '  • Mollusca: 1.5% (309K)',
            '  • + 24 phyla más: Tardigrada, Rotifera, Nematoda...',
            '',
            'Warning: 40.3% sin Class asignada (8.3M registros).',
            'Insight: GBIF mezcla ballenas con tardígrados bajo "Animalia".',
        ]
    },
    {
        'title': 'SLIDE 4 — TIMELINE',
        'subtitle': 'De 5,000 a 1.8 millones de registros por año',
        'image': 'slides/slide_04_timeline/slide_04_timeline.png',
        'desc': [
            'Objetivo: Contextualizar el crecimiento explosivo.',
            '',
            'Datos clave:',
            '  • Crecimiento exponencial desde ~2005',
            '  • Anotación en 2010: "eBird + iNaturalist"',
            '  • 2020–2024 = 7.8M registros (38% del total)',
            '  • Pico: ~1.9M en un solo año',
            '',
            'Formato: Gráfico de área con fill.',
        ]
    },
    {
        'title': 'SLIDE 5 — SESGO CIENCIA CIUDADANA',
        'subtitle': '9 de cada 10 registros son observaciones humanas',
        'image': 'slides/slide_05_sesgo/slide_05_sesgo.png',
        'desc': [
            'Objetivo: Mostrar quién observa qué.',
            '',
            'Datos clave:',
            '  • HUMAN_OBSERVATION: 89.7% (18.7M)',
            '  • MACHINE_OBSERVATION: 7.8% (1.6M)',
            '  • PRESERVED_SPECIMEN: 2.0% (425K)',
            '',
            'Contraste:',
            '  • En obs. humana: Aves 7.7M vs Insecta 67K',
            '  • En museos: Insecta 249K especímenes',
            '  • "Los insectos se conocen por museos, no ciudadanos"',
        ]
    },
    {
        'title': 'SLIDE 6 — DATOS A EXCLUIR',
        'subtitle': '1.17 millones de registros dicen "AUSENTE"',
        'image': 'slides/slide_06_absent_fossil/slide_06_absent_fossil.png',
        'desc': [
            'Objetivo: Lo que hay que sacar antes de analizar.',
            '',
            'ABSENT (occurrenceStatus):',
            '  • 1,170,113 registros (5.6%)',
            '  • Son muestreos negativos: buscaron y NO encontraron',
            '  • Si no filtras, cuenta como presencia errónea',
            '',
            'FOSSIL_SPECIMEN (basisOfRecord):',
            '  • 7,379 registros',
            '  • Incertidumbre promedio: 1,949 km',
            '  • Moluscos del Mesozoico como puntos actuales',
        ]
    },
    {
        'title': 'SLIDE 7 — INCERTIDUMBRE',
        'subtitle': '95% de registros NO reportan su precisión',
        'image': 'slides/slide_07_incertidumbre/slide_07_incertidumbre.png',
        'desc': [
            'Objetivo: Cuestionar la calidad geoespacial.',
            '',
            'Distribución coordinateUncertaintyInMeters:',
            '  • Sin dato: 19.8M (95.0%)',
            '  • 100m–1km: 694K (3.3%)',
            '  • ≤ 10m: 94K (0.5%)',
            '  • > 100km: 6,075 registros',
            '',
            'Mediana: 1 km · Máximo: 7,945 km',
        ]
    },
    {
        'title': 'SLIDE 8 — CHECKLIST METODOLÓGICO',
        'subtitle': '"Antes de mapear, filtra"',
        'image': 'slides/slide_08_checklist/slide_08_checklist.png',
        'desc': [
            'Objetivo: Dar al seguidor una guía práctica.',
            '',
            'Checklist:',
            '  ✓ Filtrar occurrenceStatus = PRESENT',
            '  ✓ Excluir FOSSIL_SPECIMEN',
            '  ✓ Revisar coordinateUncertaintyInMeters',
            '  ✓ Separar por basisOfRecord según tu pregunta',
            '  ⚠ Animalia incluye 27+ phyla, no solo vertebrados',
            '',
            'Cierre: "Un dato sin contexto es un mapa que miente"',
        ]
    },
    {
        'title': 'SLIDES 9-11 — MAPAS FILTRADOS (QGIS)',
        'subtitle': 'Datos limpios clasificados por Phylum, Class y basisOfRecord',
        'image': None,
        'desc': [
            'Objetivo: Mostrar el resultado de aplicar los filtros.',
            'Contraste visual vs. el mapa crudo de la slide 2.',
            '',
            'Slide 9 — Por Phylum:',
            '  • GeoParquet: slide_09_phylum.parquet (19.5M pts)',
            '  • Colores: Chordata / Arthropoda / Mollusca / Otros',
            '  • Nulls: 7,253 (0.03%)',
            '',
            'Slide 10 — Por Class:',
            '  • GeoParquet: slide_10_class.parquet (19.5M pts)',
            '  • Colores: Aves / Malacostraca / Mammalia / Insecta',
            '  • ⚠ 8.3M sin Class (40.3%) → gris',
            '',
            'Slide 11 — Por basisOfRecord:',
            '  • GeoParquet: slide_11_basis.parquet (19.5M pts)',
            '  • Colores: Human Obs / Machine Obs / Specimen',
            '  • Sin nulls',
            '',
            'Filtros aplicados: PRESENT only + sin FOSSIL_SPECIMEN',
            'Todos en EPSG:3857 (Pseudo-Mercator)',
            'Sugerencia: cuadrícula de densidad a 10 km',
        ]
    },
]


with PdfPages('propuesta_carrusel_conmapas.pdf') as pdf:
    for i, slide in enumerate(slides_info):
        fig = plt.figure(figsize=(W, H), dpi=DPI)
        fig.patch.set_facecolor(BG)

        # Left side: image (if available)
        if slide['image'] and os.path.exists(slide['image']):
            ax_img = fig.add_axes([0.02, 0.05, 0.42, 0.85])
            ax_img.set_facecolor(BG)
            ax_img.axis('off')
            img = Image.open(slide['image'])
            ax_img.imshow(img)
        elif i == 0:
            # Cover page — no image, center text
            pass
        else:
            ax_img = fig.add_axes([0.02, 0.05, 0.42, 0.85])
            ax_img.set_facecolor('#161b22')
            ax_img.axis('off')
            ax_img.text(0.5, 0.5, 'Mapa a realizar\nen QGIS', fontsize=14,
                       fontfamily='Segoe UI', color=GRAY_DIM, ha='center',
                       va='center', style='italic')

        # Right side: text
        text_left = 0.48 if slide['image'] or i > 0 else 0.08
        text_width = 0.48 if slide['image'] or i > 0 else 0.84

        ax_txt = fig.add_axes([text_left, 0.05, text_width, 0.85])
        ax_txt.set_facecolor(BG)
        ax_txt.axis('off')
        ax_txt.set_xlim(0, 1)
        ax_txt.set_ylim(0, 1)

        # Page number
        if i > 0:
            fig.text(0.95, 0.02, f'{i}/10', fontsize=8, fontfamily='Segoe UI',
                    color=GRAY_DIM, ha='right')

        # Title
        y = 0.95
        ax_txt.text(0, y, slide['title'], fontsize=16, fontweight='bold',
                   fontfamily='Impact', color=AMBER)
        y -= 0.06
        ax_txt.text(0, y, slide['subtitle'], fontsize=10, fontfamily='Segoe UI',
                   color=CYAN)
        y -= 0.04
        ax_txt.plot([0, 0.95], [y, y], color=GRAY_DIM, linewidth=0.5, alpha=0.5)
        y -= 0.05

        # Description lines
        for line in slide['desc']:
            if line == '':
                y -= 0.02
                continue
            if line.startswith('  '):
                color = GRAY
                fs = 8
            else:
                color = WHITE
                fs = 9
            ax_txt.text(0.02, y, line, fontsize=fs, fontfamily='Segoe UI',
                       color=color, va='top')
            y -= 0.045

        # Footer
        fig.text(0.02, 0.02, '@conmapas · GBIF Animalia Chile', fontsize=7,
                fontfamily='Segoe UI', color=GRAY_DIM, alpha=0.4)

        pdf.savefig(fig, facecolor=BG)
        plt.close()
        print(f"  Page {i+1}/{len(slides_info)}: {slide['title']}")

print("\n✅ PDF saved: propuesta_carrusel_conmapas.pdf")
