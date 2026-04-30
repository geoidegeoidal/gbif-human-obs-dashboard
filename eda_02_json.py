"""
EDA — Output results as JSON file for clean reading.
"""
import duckdb
import time
import json

CSV = "0022205-260226173443078.csv"
con = duckdb.connect()
results = {}

def query(sql):
    return con.sql(sql).fetchdf()

READ = f"read_csv('{CSV}', delim='\\t', header=true, ignore_errors=true)"

# 1. Total rows
t0 = time.perf_counter()
n = con.sql(f"SELECT COUNT(*) AS n FROM {READ}").fetchone()[0]
results["total_rows"] = int(n)
results["count_time_s"] = round(time.perf_counter() - t0, 1)

# 2. Geo stats
t0 = time.perf_counter()
df = query(f"""
SELECT
    SUM(CASE WHEN decimalLatitude IS NOT NULL AND decimalLongitude IS NOT NULL THEN 1 ELSE 0 END) AS with_coords,
    SUM(CASE WHEN decimalLatitude IS NULL OR decimalLongitude IS NULL THEN 1 ELSE 0 END) AS without_coords,
    MIN(decimalLatitude) AS lat_min, MAX(decimalLatitude) AS lat_max,
    MIN(decimalLongitude) AS lon_min, MAX(decimalLongitude) AS lon_max,
    MIN(year) AS year_min, MAX(year) AS year_max
FROM {READ}
""")
row = df.iloc[0]
results["geo"] = {k: float(v) if v == v else None for k, v in row.items()}
results["geo_time_s"] = round(time.perf_counter() - t0, 1)

# 3. Phylum
t0 = time.perf_counter()
df = query(f"SELECT phylum, COUNT(*) AS n FROM {READ} GROUP BY phylum ORDER BY n DESC LIMIT 15")
results["phylum_top15"] = [{"phylum": str(r["phylum"]), "n": int(r["n"])} for _, r in df.iterrows()]
results["phylum_time_s"] = round(time.perf_counter() - t0, 1)

# 4. Class
t0 = time.perf_counter()
df = query(f"SELECT class, COUNT(*) AS n FROM {READ} GROUP BY class ORDER BY n DESC LIMIT 15")
results["class_top15"] = [{"class": str(r["class"]), "n": int(r["n"])} for _, r in df.iterrows()]
results["class_time_s"] = round(time.perf_counter() - t0, 1)

# 5. basisOfRecord
t0 = time.perf_counter()
df = query(f"SELECT basisOfRecord, COUNT(*) AS n FROM {READ} GROUP BY basisOfRecord ORDER BY n DESC")
results["basisOfRecord"] = [{"basis": str(r["basisOfRecord"]), "n": int(r["n"])} for _, r in df.iterrows()]
results["basis_time_s"] = round(time.perf_counter() - t0, 1)

# 6. stateProvince top 20
t0 = time.perf_counter()
df = query(f"SELECT stateProvince, COUNT(*) AS n FROM {READ} GROUP BY stateProvince ORDER BY n DESC LIMIT 20")
results["province_top20"] = [{"province": str(r["stateProvince"]), "n": int(r["n"])} for _, r in df.iterrows()]
results["province_time_s"] = round(time.perf_counter() - t0, 1)

# 7. Year distribution >= 1970
t0 = time.perf_counter()
df = query(f"SELECT year, COUNT(*) AS n FROM {READ} WHERE year IS NOT NULL AND year >= 1970 GROUP BY year ORDER BY year")
results["year_dist"] = [{"year": int(r["year"]), "n": int(r["n"])} for _, r in df.iterrows()]
results["year_time_s"] = round(time.perf_counter() - t0, 1)

# 8. Null analysis
t0 = time.perf_counter()
df = query(f"""
SELECT
    SUM(CASE WHEN species IS NULL OR species = '' THEN 1 ELSE 0 END) AS species_null,
    SUM(CASE WHEN genus IS NULL OR genus = '' THEN 1 ELSE 0 END) AS genus_null,
    SUM(CASE WHEN family IS NULL OR family = '' THEN 1 ELSE 0 END) AS family_null,
    SUM(CASE WHEN "order" IS NULL OR "order" = '' THEN 1 ELSE 0 END) AS order_null,
    SUM(CASE WHEN class IS NULL OR class = '' THEN 1 ELSE 0 END) AS class_null,
    SUM(CASE WHEN phylum IS NULL OR phylum = '' THEN 1 ELSE 0 END) AS phylum_null,
    SUM(CASE WHEN eventDate IS NULL OR CAST(eventDate AS VARCHAR) = '' THEN 1 ELSE 0 END) AS date_null,
    SUM(CASE WHEN decimalLatitude IS NULL THEN 1 ELSE 0 END) AS lat_null,
    SUM(CASE WHEN decimalLongitude IS NULL THEN 1 ELSE 0 END) AS lon_null
FROM {READ}
""")
row = df.iloc[0]
total = results["total_rows"]
results["nulls"] = {k: {"count": int(v), "pct": round(float(v) / total * 100, 1)} for k, v in row.items()}
results["nulls_time_s"] = round(time.perf_counter() - t0, 1)

# 9. Schema
df = query(f"DESCRIBE SELECT * FROM {READ}")
results["schema"] = [{"col": r["column_name"], "type": r["column_type"]} for _, r in df.iterrows()]

with open("eda_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("DONE - results in eda_results.json")
