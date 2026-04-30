"""
EDA Step 2 — Análisis metodológico profundo.
Cuantifica sesgos de basisOfRecord, incertidumbre de coordenadas,
occurrenceStatus, fósiles, y distribución taxonómica real.
"""
import duckdb
import json
import time

CSV = "0022205-260226173443078.csv"
con = duckdb.connect()
READ = f"read_csv('{CSV}', delim='\\t', header=true, ignore_errors=true)"
results = {}

# 1. occurrenceStatus breakdown
t0 = time.perf_counter()
df = con.sql(f"""
    SELECT occurrenceStatus, COUNT(*) AS n
    FROM {READ}
    GROUP BY occurrenceStatus ORDER BY n DESC
""").fetchdf()
results["occurrenceStatus"] = [{"status": str(r["occurrenceStatus"]), "n": int(r["n"])} for _, r in df.iterrows()]
results["occurrenceStatus_time"] = round(time.perf_counter() - t0, 1)

# 2. coordinateUncertaintyInMeters distribution
t0 = time.perf_counter()
df = con.sql(f"""
    SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN coordinateUncertaintyInMeters IS NULL THEN 1 ELSE 0 END) AS sin_incertidumbre,
        SUM(CASE WHEN coordinateUncertaintyInMeters <= 10 THEN 1 ELSE 0 END) AS hasta_10m,
        SUM(CASE WHEN coordinateUncertaintyInMeters > 10 AND coordinateUncertaintyInMeters <= 100 THEN 1 ELSE 0 END) AS "10_100m",
        SUM(CASE WHEN coordinateUncertaintyInMeters > 100 AND coordinateUncertaintyInMeters <= 1000 THEN 1 ELSE 0 END) AS "100_1000m",
        SUM(CASE WHEN coordinateUncertaintyInMeters > 1000 AND coordinateUncertaintyInMeters <= 10000 THEN 1 ELSE 0 END) AS "1_10km",
        SUM(CASE WHEN coordinateUncertaintyInMeters > 10000 AND coordinateUncertaintyInMeters <= 100000 THEN 1 ELSE 0 END) AS "10_100km",
        SUM(CASE WHEN coordinateUncertaintyInMeters > 100000 THEN 1 ELSE 0 END) AS "mas_100km",
        ROUND(AVG(coordinateUncertaintyInMeters), 1) AS promedio_m,
        ROUND(MEDIAN(coordinateUncertaintyInMeters), 1) AS mediana_m,
        MIN(coordinateUncertaintyInMeters) AS min_m,
        MAX(coordinateUncertaintyInMeters) AS max_m
    FROM {READ}
""").fetchdf()
row = df.iloc[0]
results["coord_uncertainty"] = {k: float(v) if v == v else None for k, v in row.items()}
results["coord_uncertainty_time"] = round(time.perf_counter() - t0, 1)

# 3. FOSSIL_SPECIMEN analysis
t0 = time.perf_counter()
df = con.sql(f"""
    SELECT phylum, class, COUNT(*) AS n
    FROM {READ}
    WHERE basisOfRecord = 'FOSSIL_SPECIMEN'
    GROUP BY phylum, class ORDER BY n DESC LIMIT 20
""").fetchdf()
results["fossil_taxonomy"] = [{"phylum": str(r["phylum"]), "class": str(r["class"]), "n": int(r["n"])} for _, r in df.iterrows()]

# Fossil geo extent
df2 = con.sql(f"""
    SELECT
        COUNT(*) AS n,
        MIN(decimalLatitude) AS lat_min, MAX(decimalLatitude) AS lat_max,
        MIN(decimalLongitude) AS lon_min, MAX(decimalLongitude) AS lon_max,
        MIN(year) AS year_min, MAX(year) AS year_max
    FROM {READ}
    WHERE basisOfRecord = 'FOSSIL_SPECIMEN'
""").fetchdf()
row2 = df2.iloc[0]
results["fossil_geo"] = {k: float(v) if v == v else None for k, v in row2.items()}
results["fossil_time"] = round(time.perf_counter() - t0, 1)

# 4. HUMAN_OBSERVATION breakdown by class (sesgo de ciencia ciudadana)
t0 = time.perf_counter()
df = con.sql(f"""
    SELECT class, COUNT(*) AS n
    FROM {READ}
    WHERE basisOfRecord = 'HUMAN_OBSERVATION'
    GROUP BY class ORDER BY n DESC LIMIT 15
""").fetchdf()
results["human_obs_class"] = [{"class": str(r["class"]), "n": int(r["n"])} for _, r in df.iterrows()]
results["human_obs_time"] = round(time.perf_counter() - t0, 1)

# 5. Registros por basisOfRecord × phylum (para entender composición)
t0 = time.perf_counter()
df = con.sql(f"""
    SELECT basisOfRecord, phylum, COUNT(*) AS n
    FROM {READ}
    GROUP BY basisOfRecord, phylum ORDER BY basisOfRecord, n DESC
""").fetchdf()
results["basis_phylum"] = [{"basis": str(r["basisOfRecord"]), "phylum": str(r["phylum"]), "n": int(r["n"])} for _, r in df.iterrows()]
results["basis_phylum_time"] = round(time.perf_counter() - t0, 1)

# 6. Insecta vs Aves vs Mammalia (quién domina realmente)
t0 = time.perf_counter()
df = con.sql(f"""
    SELECT class, basisOfRecord, COUNT(*) AS n
    FROM {READ}
    WHERE class IN ('Aves', 'Insecta', 'Mammalia', 'Malacostraca', 'Actinopterygii',
                     'Elasmobranchii', 'Reptilia', 'Amphibia', 'Arachnida', 'Gastropoda')
    GROUP BY class, basisOfRecord ORDER BY class, n DESC
""").fetchdf()
results["key_classes_by_basis"] = [{"class": str(r["class"]), "basis": str(r["basisOfRecord"]), "n": int(r["n"])} for _, r in df.iterrows()]
results["key_classes_time"] = round(time.perf_counter() - t0, 1)

# 7. Registros con coordinateUncertaintyInMeters > 10km por basisOfRecord
t0 = time.perf_counter()
df = con.sql(f"""
    SELECT basisOfRecord, COUNT(*) AS n,
        ROUND(AVG(coordinateUncertaintyInMeters), 0) AS avg_uncertainty_m
    FROM {READ}
    WHERE coordinateUncertaintyInMeters > 10000
    GROUP BY basisOfRecord ORDER BY n DESC
""").fetchdf()
results["high_uncertainty_by_basis"] = [{"basis": str(r["basisOfRecord"]), "n": int(r["n"]), "avg_m": float(r["avg_uncertainty_m"])} for _, r in df.iterrows()]
results["high_uncertainty_time"] = round(time.perf_counter() - t0, 1)

# 8. Phylum real count excluyendo Chordata y Arthropoda
t0 = time.perf_counter()
df = con.sql(f"""
    SELECT phylum, COUNT(*) AS n
    FROM {READ}
    WHERE phylum NOT IN ('Chordata', 'Arthropoda')
    GROUP BY phylum ORDER BY n DESC
""").fetchdf()
results["minor_phyla"] = [{"phylum": str(r["phylum"]), "n": int(r["n"])} for _, r in df.iterrows()]
results["minor_phyla_time"] = round(time.perf_counter() - t0, 1)

with open("eda_methodological.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("DONE - results in eda_methodological.json")
