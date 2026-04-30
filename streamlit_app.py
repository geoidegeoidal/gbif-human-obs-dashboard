"""
Streamlit Cloud launcher.
Ejecuta automáticamente el dashboard desde la raíz del repo.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import runpy
runpy.run_path(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard", "app.py"),
    run_name="__main__"
)
