"""
Precomputa datasets agregados desde el CSV original (11 GB)
para que el dashboard funcione en Streamlit Cloud (1 GB RAM).
Genera archivos JSON/Parquet livianos en dashboard/data/precomputed/.
"""

import duckdb
import json
import os
import time
import numpy as np
from config import CSV_PATH, PQ_PATH, PRECOMPUTE_DIR


def precompute_all():
    """Genera todos los datasets precomputados."""
    os.makedirs(PRECOMPUTE_DIR, exist_ok=True)
    con = duckdb.connect()

    # Forzar CSV porque map_data.parquet no tiene species, genus, family, etc.
    if os.path.exists(CSV_PATH):
        src = f"read_csv('{CSV_PATH}', delim='\\t', header=true, ignore_errors=true)"
        print(f"Usando CSV: {CSV_PATH}")
    else:
        src = f"'{PQ_PATH}'"
        print(f"CSV no encontrado, usando Parquet: {PQ_PATH}")

    results = {}

    def save_json(name, data):
        path = os.path.join(PRECOMPUTE_DIR, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"  -> {name}.json ({len(str(data))} bytes)")

    def save_parquet(name, df):
        path = os.path.join(PRECOMPUTE_DIR, f"{name}.parquet")
        df.to_parquet(path)
        size_kb = os.path.getsize(path) / 1024
        print(f"  -> {name}.parquet ({size_kb:.0f} KB, {len(df)} rows)")

    # 1. KPIs
    t0 = time.perf_counter()
    print("\n1. KPIs...")
    kpi = con.sql(f"""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN basisOfRecord = 'HUMAN_OBSERVATION' THEN 1 ELSE 0 END) AS human_obs,
            SUM(CASE WHEN decimalLatitude IS NOT NULL AND decimalLongitude IS NOT NULL
                 THEN 1 ELSE 0 END) AS with_coords,
            SUM(CASE WHEN occurrenceStatus = 'ABSENT' THEN 1 ELSE 0 END) AS absent,
            SUM(CASE WHEN basisOfRecord = 'FOSSIL_SPECIMEN' THEN 1 ELSE 0 END) AS fossil
        FROM {src}
    """).fetchdf().iloc[0]
    results["kpi"] = {k: int(v) for k, v in kpi.items()}
    results["kpi_time"] = round(time.perf_counter() - t0, 1)
    save_json("kpi", results["kpi"])

    # 2. Phylum distribution (all + human obs)
    t0 = time.perf_counter()
    print("\n2. Phylum distribution...")
    for label, where in [("phylum_all", ""), ("phylum_human", "WHERE basisOfRecord = 'HUMAN_OBSERVATION'")]:
        df = con.sql(f"""
            SELECT phylum, COUNT(*) AS n
            FROM {src}
            {where}
            GROUP BY phylum ORDER BY n DESC
        """).fetchdf()
        df["phylum"] = df["phylum"].fillna("Sin dato")
        data = [{"phylum": str(r["phylum"]), "n": int(r["n"])} for _, r in df.iterrows()]
        save_json(label, data)
    results["phylum_time"] = round(time.perf_counter() - t0, 1)

    # 3. Class distribution
    t0 = time.perf_counter()
    print("\n3. Class distribution...")
    for label, where in [
        ("class_all", ""),
        ("class_human", "WHERE basisOfRecord = 'HUMAN_OBSERVATION'"),
    ]:
        df = con.sql(f"""
            SELECT class, phylum, COUNT(*) AS n
            FROM {src}
            {where}
            GROUP BY class, phylum ORDER BY n DESC
            LIMIT 100
        """).fetchdf()
        df["class"] = df["class"].fillna("Sin dato")
        df["phylum"] = df["phylum"].fillna("Sin dato")
        data = [{"class": str(r["class"]), "phylum": str(r["phylum"]), "n": int(r["n"])} for _, r in df.iterrows()]
        save_json(label, data)
    results["class_time"] = round(time.perf_counter() - t0, 1)

    # 4. Top species (human obs)
    t0 = time.perf_counter()
    print("\n4. Top species...")
    df = con.sql(f"""
        SELECT species, class, COUNT(*) AS n
        FROM {src}
        WHERE basisOfRecord = 'HUMAN_OBSERVATION'
          AND species IS NOT NULL AND species != ''
        GROUP BY species, class ORDER BY n DESC
        LIMIT 30
    """).fetchdf()
    data = [{"species": str(r["species"]), "class": str(r["class"]), "n": int(r["n"])} for _, r in df.iterrows()]
    save_json("top_species", data)
    results["species_time"] = round(time.perf_counter() - t0, 1)

    # 5. Aves vs Insecta in human obs
    t0 = time.perf_counter()
    print("\n5. Aves vs Insecta...")
    df = con.sql(f"""
        SELECT class, COUNT(*) AS n
        FROM {src}
        WHERE basisOfRecord = 'HUMAN_OBSERVATION'
          AND class IN ('Aves', 'Insecta')
        GROUP BY class
    """).fetchdf()
    data = [{"class": str(r["class"]), "n": int(r["n"])} for _, r in df.iterrows()]
    save_json("aves_insecta", data)
    results["aves_time"] = round(time.perf_counter() - t0, 1)

    # 6. Year distribution
    t0 = time.perf_counter()
    print("\n6. Year distribution...")
    for label, basis in [("year_all", None), ("year_human", "HUMAN_OBSERVATION")]:
        where = "WHERE year IS NOT NULL AND year >= 1950"
        if basis:
            where += f" AND basisOfRecord = '{basis}'"
        df = con.sql(f"""
            SELECT year, COUNT(*) AS n
            FROM {src}
            {where}
            GROUP BY year ORDER BY year
        """).fetchdf()
        data = [{"year": int(r["year"]), "n": int(r["n"])} for _, r in df.iterrows()]
        save_json(label, data)
    results["year_time"] = round(time.perf_counter() - t0, 1)

    # 7. Month distribution (human obs)
    t0 = time.perf_counter()
    print("\n7. Month distribution...")
    df = con.sql(f"""
        SELECT month, COUNT(*) AS n
        FROM {src}
        WHERE month IS NOT NULL
          AND basisOfRecord = 'HUMAN_OBSERVATION'
          AND year >= 2000
        GROUP BY month ORDER BY month
    """).fetchdf()
    data = [{"month": int(r["month"]), "n": int(r["n"])} for _, r in df.iterrows()]
    save_json("month_dist", data)
    results["month_time"] = round(time.perf_counter() - t0, 1)

    # 8. Basis of record
    t0 = time.perf_counter()
    print("\n8. Basis of record...")
    df = con.sql(f"""
        SELECT basisOfRecord AS basis, COUNT(*) AS n
        FROM {src}
        GROUP BY basisOfRecord ORDER BY n DESC
    """).fetchdf()
    data = [{"basis": str(r["basis"]), "n": int(r["n"])} for _, r in df.iterrows()]
    save_json("basis_dist", data)
    results["basis_time"] = round(time.perf_counter() - t0, 1)

    # 9. Coordinate uncertainty
    t0 = time.perf_counter()
    print("\n9. Coordinate uncertainty...")
    unc = con.sql(f"""
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
            SUM(CASE WHEN coordinateUncertaintyInMeters > 100000 THEN 1 ELSE 0 END) AS mas_100km,
            AVG(coordinateUncertaintyInMeters) AS promedio_m,
            MEDIAN(coordinateUncertaintyInMeters) AS mediana_m
        FROM {src}
    """).fetchdf().iloc[0]
    data = {k: (float(v) if v == v else None) for k, v in unc.items()}
    save_json("uncertainty", data)
    results["unc_time"] = round(time.perf_counter() - t0, 1)

    # 10. Completeness
    t0 = time.perf_counter()
    print("\n10. Field completeness...")
    comp = con.sql(f"""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN species IS NOT NULL AND species != '' THEN 1 ELSE 0 END) AS species_ok,
            SUM(CASE WHEN genus IS NOT NULL AND genus != '' THEN 1 ELSE 0 END) AS genus_ok,
            SUM(CASE WHEN family IS NOT NULL AND family != '' THEN 1 ELSE 0 END) AS family_ok,
            SUM(CASE WHEN "order" IS NOT NULL AND "order" != '' THEN 1 ELSE 0 END) AS order_ok,
            SUM(CASE WHEN class IS NOT NULL AND class != '' THEN 1 ELSE 0 END) AS class_ok,
            SUM(CASE WHEN phylum IS NOT NULL AND phylum != '' THEN 1 ELSE 0 END) AS phylum_ok,
            SUM(CASE WHEN eventDate IS NOT NULL AND CAST(eventDate AS VARCHAR) != '' THEN 1 ELSE 0 END) AS date_ok
        FROM {src}
    """).fetchdf().iloc[0]
    data = {k: int(v) for k, v in comp.items()}
    save_json("completeness", data)
    results["comp_time"] = round(time.perf_counter() - t0, 1)

    # 11. State province
    t0 = time.perf_counter()
    print("\n11. State province...")
    df = con.sql(f"""
        SELECT stateProvince AS provincia, COUNT(*) AS n
        FROM {src}
        WHERE stateProvince IS NOT NULL AND stateProvince != ''
          AND basisOfRecord = 'HUMAN_OBSERVATION'
        GROUP BY stateProvince ORDER BY n DESC
    """).fetchdf()
    data = [{"provincia": str(r["provincia"]), "n": int(r["n"])} for _, r in df.iterrows()]
    save_json("provincia_dist", data)
    results["prov_time"] = round(time.perf_counter() - t0, 1)

    # 12. Human obs sample coords for map (50K)
    t0 = time.perf_counter()
    print("\n12. Sample coordinates for maps...")
    df = con.sql(f"""
        SELECT decimalLatitude AS lat, decimalLongitude AS lon, phylum, class, year
        FROM {src}
        WHERE decimalLatitude IS NOT NULL
          AND decimalLongitude IS NOT NULL
          AND basisOfRecord = 'HUMAN_OBSERVATION'
        USING SAMPLE 50000
    """).fetchdf()
    save_parquet("coords_sample", df)
    results["sample_time"] = round(time.perf_counter() - t0, 1)

    # Save summary
    results["status"] = "ok"
    save_json("_summary", results)

    print(f"\n{'='*50}")
    print(f"Precomputo completo en {PRECOMPUTE_DIR}")
    for k, v in results.items():
        if k.endswith("_time"):
            print(f"  {k}: {v}s")
    print(f"{'='*50}")


if __name__ == "__main__":
    precompute_all()
