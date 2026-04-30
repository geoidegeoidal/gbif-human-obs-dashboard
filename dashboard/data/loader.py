"""
Data loader para el dashboard.
Prioriza datos precomputados (JSON/Parquet), con fallback a DuckDB queries.
"""

import json
import os
import pandas as pd
from dashboard.config import PRECOMPUTE_DIR


def load_json(name):
    """Carga un archivo JSON precomputado."""
    path = os.path.join(PRECOMPUTE_DIR, f"{name}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def load_parquet(name):
    """Carga un archivo Parquet precomputado."""
    path = os.path.join(PRECOMPUTE_DIR, f"{name}.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    return None


def has_precomputed():
    """Verifica si existen datos precomputados."""
    return os.path.exists(os.path.join(PRECOMPUTE_DIR, "_summary.json"))


def get_data(key, query_fn=None):
    """
    Obtiene datos: primero intenta precomputados, luego ejecuta query_fn (si se pasó).
    Retorna (data, source) donde source es 'json', 'parquet', 'query', o 'none'.
    """
    # Intentar JSON
    json_data = load_json(key)
    if json_data is not None:
        return json_data, "json"

    # Intentar Parquet
    pq_data = load_parquet(key)
    if pq_data is not None:
        return pq_data, "parquet"

    # Ejecutar query en vivo
    if query_fn:
        return query_fn(), "query"

    return None, "none"
