"""
Catálogo de consultas DuckDB para el dashboard.
Usa el CSV original (11 GB) o el Parquet intermedio según disponibilidad.
"""

import duckdb
import os
import pandas as pd
from config import CSV_PATH, PQ_PATH, GEOPQ_DIR, PRECOMPUTE_DIR


class Queries:
    """Encapsula todas las consultas DuckDB reutilizables."""

    def __init__(self, use_parquet=True):
        self.con = duckdb.connect()
        if use_parquet and os.path.exists(PQ_PATH):
            self._src = f"'{PQ_PATH}'"
            self._src_type = "parquet"
        elif os.path.exists(CSV_PATH):
            self._src = f"read_csv('{CSV_PATH}', delim='\\t', header=true, ignore_errors=true)"
            self._src_type = "csv"
        else:
            self._src = None
            self._src_type = "none"
        self._cache = {}

    @property
    def src(self):
        if self._src is None:
            raise FileNotFoundError(
                f"No se encontraron datos. Busqué:\n"
                f"  - Parquet: {PQ_PATH}\n"
                f"  - CSV: {CSV_PATH}"
            )
        return self._src

    def _query(self, sql, cache_key=None):
        """Ejecuta consulta con caché opcional."""
        if cache_key and cache_key in self._cache:
            return self._cache[cache_key]
        df = self.con.sql(sql).fetchdf()
        if cache_key:
            self._cache[cache_key] = df
        return df

    # ---- KPIs ----

    def kpi_totals(self):
        """Total de registros, human obs, con coords."""
        sql = f"""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN basisOfRecord = 'HUMAN_OBSERVATION' THEN 1 ELSE 0 END) AS human_obs,
                SUM(CASE WHEN decimalLatitude IS NOT NULL AND decimalLongitude IS NOT NULL
                     THEN 1 ELSE 0 END) AS with_coords,
                SUM(CASE WHEN occurrenceStatus = 'ABSENT' THEN 1 ELSE 0 END) AS absent,
                SUM(CASE WHEN basisOfRecord = 'FOSSIL_SPECIMEN' THEN 1 ELSE 0 END) AS fossil
            FROM {self.src}
        """
        return self._query(sql, "kpi_totals").iloc[0]

    # ---- Taxonomía ----

    def phylum_distribution(self, basis_filter=None):
        """Distribución de phyla. Opcional filtrar por basisOfRecord."""
        where = ""
        if basis_filter:
            where = f"WHERE basisOfRecord = '{basis_filter}'"
        sql = f"""
            SELECT phylum, COUNT(*) AS n
            FROM {self.src}
            {where}
            GROUP BY phylum
            ORDER BY n DESC
        """
        return self._query(sql, f"phylum_{basis_filter or 'all'}")

    def class_distribution(self, basis_filter=None):
        """Distribución de clases."""
        where = ""
        if basis_filter:
            where = f"WHERE basisOfRecord = '{basis_filter}'"
        sql = f"""
            SELECT class, phylum, COUNT(*) AS n
            FROM {self.src}
            {where}
            GROUP BY class, phylum
            ORDER BY n DESC
        """
        return self._query(sql, f"class_{basis_filter or 'all'}")

    def top_species(self, limit=20, basis_filter="HUMAN_OBSERVATION"):
        """Top especies en observaciones humanas."""
        sql = f"""
            SELECT species, class, COUNT(*) AS n
            FROM {self.src}
            WHERE basisOfRecord = '{basis_filter}'
              AND species IS NOT NULL AND species != ''
            GROUP BY species, class
            ORDER BY n DESC
            LIMIT {limit}
        """
        return self._query(sql, f"top_species_{limit}")

    def aves_vs_insecta_human_obs(self):
        """Comparación Aves vs Insecta en human observations."""
        sql = f"""
            SELECT class, COUNT(*) AS n
            FROM {self.src}
            WHERE basisOfRecord = 'HUMAN_OBSERVATION'
              AND class IN ('Aves', 'Insecta')
            GROUP BY class
        """
        return self._query(sql, "aves_vs_insecta")

    def insecta_by_basis(self):
        """Insecta desglosado por basisOfRecord."""
        sql = f"""
            SELECT basisOfRecord, COUNT(*) AS n
            FROM {self.src}
            WHERE class = 'Insecta'
            GROUP BY basisOfRecord
            ORDER BY n DESC
        """
        return self._query(sql, "insecta_by_basis")

    # ---- Espacialidad ----

    def state_province_distribution(self, basis_filter=None):
        """Distribución por stateProvince."""
        where = "WHERE stateProvince IS NOT NULL AND stateProvince != ''"
        if basis_filter:
            where += f" AND basisOfRecord = '{basis_filter}'"
        sql = f"""
            SELECT
                stateProvince AS provincia,
                COUNT(*) AS n
            FROM {self.src}
            {where}
            GROUP BY stateProvince
            ORDER BY n DESC
        """
        return self._query(sql, f"province_{basis_filter or 'all'}")

    def coordinate_bounds(self):
        """Bounds de coordenadas para centrar mapas."""
        sql = f"""
            SELECT
                MIN(decimalLatitude) AS lat_min,
                MAX(decimalLatitude) AS lat_max,
                MIN(decimalLongitude) AS lon_min,
                MAX(decimalLongitude) AS lon_max
            FROM {self.src}
            WHERE decimalLatitude IS NOT NULL
              AND decimalLongitude IS NOT NULL
        """
        return self._query(sql, "bounds").iloc[0]

    # ---- Temporalidad ----

    def year_distribution(self, basis_filter="HUMAN_OBSERVATION", min_year=1970):
        """Distribución anual."""
        sql = f"""
            SELECT year, COUNT(*) AS n
            FROM {self.src}
            WHERE year IS NOT NULL
              AND year >= {min_year}
              AND basisOfRecord = '{basis_filter}'
            GROUP BY year
            ORDER BY year
        """
        return self._query(sql, f"year_{basis_filter}_{min_year}")

    def month_distribution(self, basis_filter="HUMAN_OBSERVATION"):
        """Distribución mensual."""
        sql = f"""
            SELECT month, COUNT(*) AS n
            FROM {self.src}
            WHERE month IS NOT NULL
              AND basisOfRecord = '{basis_filter}'
            GROUP BY month
            ORDER BY month
        """
        return self._query(sql, f"month_{basis_filter}")

    # ---- Calidad de datos ----

    def coordinate_uncertainty_distribution(self):
        """Distribución de coordinateUncertaintyInMeters."""
        sql = f"""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN coordinateUncertaintyInMeters IS NULL THEN 1 ELSE 0 END) AS sin_dato,
                SUM(CASE WHEN coordinateUncertaintyInMeters <= 10 THEN 1 ELSE 0 END) AS hasta_10m,
                SUM(CASE WHEN coordinateUncertaintyInMeters > 10
                         AND coordinateUncertaintyInMeters <= 100 THEN 1 ELSE 0 END) AS de_10_100m,
                SUM(CASE WHEN coordinateUncertaintyInMeters > 100
                         AND coordinateUncertaintyInMeters <= 1000 THEN 1 ELSE 0 END) AS de_100_1000m,
                SUM(CASE WHEN coordinateUncertaintyInMeters > 1000
                         AND coordinateUncertaintyInMeters <= 10000 THEN 1 ELSE 0 END) AS de_1_10km,
                SUM(CASE WHEN coordinateUncertaintyInMeters > 10000
                         AND coordinateUncertaintyInMeters <= 100000 THEN 1 ELSE 0 END) AS de_10_100km,
                SUM(CASE WHEN coordinateUncertaintyInMeters > 100000 THEN 1 ELSE 0 END) AS mas_100km
            FROM {self.src}
        """
        return self._query(sql, "uncertainty").iloc[0]

    def completeness_fields(self):
        """Completitud de campos taxonómicos clave."""
        sql = f"""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN species IS NOT NULL AND species != '' THEN 1 ELSE 0 END) AS species_ok,
                SUM(CASE WHEN genus IS NOT NULL AND genus != '' THEN 1 ELSE 0 END) AS genus_ok,
                SUM(CASE WHEN family IS NOT NULL AND family != '' THEN 1 ELSE 0 END) AS family_ok,
                SUM(CASE WHEN "order" IS NOT NULL AND "order" != '' THEN 1 ELSE 0 END) AS order_ok,
                SUM(CASE WHEN class IS NOT NULL AND class != '' THEN 1 ELSE 0 END) AS class_ok,
                SUM(CASE WHEN phylum IS NOT NULL AND phylum != '' THEN 1 ELSE 0 END) AS phylum_ok,
                SUM(CASE WHEN eventDate IS NOT NULL
                         AND CAST(eventDate AS VARCHAR) != '' THEN 1 ELSE 0 END) AS date_ok
            FROM {self.src}
        """
        return self._query(sql, "completeness").iloc[0]

    def basis_of_record_distribution(self):
        """Distribución por basisOfRecord."""
        sql = f"""
            SELECT basisOfRecord, COUNT(*) AS n
            FROM {self.src}
            GROUP BY basisOfRecord
            ORDER BY n DESC
        """
        return self._query(sql, "basis_dist")

    def sample_coords(self, n=50000, basis_filter="HUMAN_OBSERVATION"):
        """Muestra de coordenadas para mapas (limitar a N puntos)."""
        sql = f"""
            SELECT decimalLatitude AS lat, decimalLongitude AS lon, phylum, class, year
            FROM {self.src}
            WHERE decimalLatitude IS NOT NULL
              AND decimalLongitude IS NOT NULL
              AND basisOfRecord = '{basis_filter}'
            USING SAMPLE {n}
        """
        return self._query(sql, f"sample_{n}_{basis_filter}")


# Singleton
_queries_instance = None


def get_queries() -> Queries:
    global _queries_instance
    if _queries_instance is None:
        _queries_instance = Queries()
    return _queries_instance
