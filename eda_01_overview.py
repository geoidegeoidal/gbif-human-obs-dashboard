"""
EDA Step 1 — Overview rápido del dataset GBIF Animalia (~20.8M filas, ~11 GB)
Usa DuckDB para escanear el CSV en disco sin cargar en RAM.
"""

import duckdb
import time

CSV = r"0022205-260226173443078.csv"

con = duckdb.connect()

# ---------- 1. Conteo total ----------
t0 = time.perf_counter()
row_count = con.sql(f"""
    SELECT COUNT(*) AS n FROM read_csv('{CSV}', delim='\t', header=true, ignore_errors=true)
""").fetchone()[0]
t1 = time.perf_counter()
print(f"✅ Total de registros: {row_count:,.0f}  ({t1 - t0:.1f}s)")

# ---------- 2. Columnas y tipos ----------
schema = con.sql(f"""
    DESCRIBE SELECT * FROM read_csv('{CSV}', delim='\t', header=true, ignore_errors=true)
""").fetchdf()
print(f"\n📋 Columnas ({len(schema)}):")
for _, r in schema.iterrows():
    print(f"   {r['column_name']:40s}  {r['column_type']}")

# ---------- 3. Registros con coordenadas válidas ----------
t0 = time.perf_counter()
geo_stats = con.sql(f"""
    SELECT
        COUNT(*) AS total,
        COUNT(decimalLatitude) AS con_lat,
        COUNT(decimalLongitude) AS con_lon,
        SUM(CASE WHEN decimalLatitude IS NOT NULL AND decimalLongitude IS NOT NULL THEN 1 ELSE 0 END) AS con_ambas,
        MIN(decimalLatitude) AS lat_min, MAX(decimalLatitude) AS lat_max,
        MIN(decimalLongitude) AS lon_min, MAX(decimalLongitude) AS lon_max,
        MIN(year) AS year_min, MAX(year) AS year_max
    FROM read_csv('{CSV}', delim='\t', header=true, ignore_errors=true)
""").fetchdf()
t1 = time.perf_counter()
print(f"\n🌍 Coordenadas y rango temporal ({t1 - t0:.1f}s):")
for col in geo_stats.columns:
    print(f"   {col:30s}: {geo_stats[col].iloc[0]}")

# ---------- 4. Top 10 Phylum ----------
t0 = time.perf_counter()
phylum = con.sql(f"""
    SELECT phylum, COUNT(*) AS n
    FROM read_csv('{CSV}', delim='\t', header=true, ignore_errors=true)
    GROUP BY phylum ORDER BY n DESC LIMIT 15
""").fetchdf()
t1 = time.perf_counter()
print(f"\n🔬 Top 15 Phylum ({t1 - t0:.1f}s):")
for _, r in phylum.iterrows():
    print(f"   {str(r['phylum']):30s} {r['n']:>12,.0f}")

# ---------- 5. Top 10 Class ----------
t0 = time.perf_counter()
clase = con.sql(f"""
    SELECT class, COUNT(*) AS n
    FROM read_csv('{CSV}', delim='\t', header=true, ignore_errors=true)
    GROUP BY class ORDER BY n DESC LIMIT 15
""").fetchdf()
t1 = time.perf_counter()
print(f"\n🦎 Top 15 Class ({t1 - t0:.1f}s):")
for _, r in clase.iterrows():
    print(f"   {str(r['class']):30s} {r['n']:>12,.0f}")

# ---------- 6. basisOfRecord ----------
t0 = time.perf_counter()
basis = con.sql(f"""
    SELECT basisOfRecord, COUNT(*) AS n
    FROM read_csv('{CSV}', delim='\t', header=true, ignore_errors=true)
    GROUP BY basisOfRecord ORDER BY n DESC
""").fetchdf()
t1 = time.perf_counter()
print(f"\n📦 basisOfRecord ({t1 - t0:.1f}s):")
for _, r in basis.iterrows():
    print(f"   {str(r['basisOfRecord']):30s} {r['n']:>12,.0f}")

# ---------- 7. stateProvince top 20 ----------
t0 = time.perf_counter()
prov = con.sql(f"""
    SELECT stateProvince, COUNT(*) AS n
    FROM read_csv('{CSV}', delim='\t', header=true, ignore_errors=true)
    GROUP BY stateProvince ORDER BY n DESC LIMIT 20
""").fetchdf()
t1 = time.perf_counter()
print(f"\n🗺️ Top 20 stateProvince ({t1 - t0:.1f}s):")
for _, r in prov.iterrows():
    print(f"   {str(r['stateProvince']):40s} {r['n']:>12,.0f}")

# ---------- 8. Distribución por año (últimos 50 años) ----------
t0 = time.perf_counter()
years = con.sql(f"""
    SELECT year, COUNT(*) AS n
    FROM read_csv('{CSV}', delim='\t', header=true, ignore_errors=true)
    WHERE year IS NOT NULL AND year >= 1970
    GROUP BY year ORDER BY year
""").fetchdf()
t1 = time.perf_counter()
print(f"\n📅 Registros por año >= 1970 ({t1 - t0:.1f}s):")
for _, r in years.iterrows():
    yr = r['year']
    print(f"   {int(yr) if yr == yr else '?':>6}  {r['n']:>10,.0f}")

# ---------- 9. Nulidad de campos clave ----------
t0 = time.perf_counter()
nulls = con.sql(f"""
    SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN species IS NULL OR species = '' THEN 1 ELSE 0 END) AS species_null,
        SUM(CASE WHEN genus IS NULL OR genus = '' THEN 1 ELSE 0 END) AS genus_null,
        SUM(CASE WHEN family IS NULL OR family = '' THEN 1 ELSE 0 END) AS family_null,
        SUM(CASE WHEN "order" IS NULL OR "order" = '' THEN 1 ELSE 0 END) AS order_null,
        SUM(CASE WHEN class IS NULL OR class = '' THEN 1 ELSE 0 END) AS class_null,
        SUM(CASE WHEN phylum IS NULL OR phylum = '' THEN 1 ELSE 0 END) AS phylum_null,
        SUM(CASE WHEN eventDate IS NULL OR eventDate = '' THEN 1 ELSE 0 END) AS date_null,
        SUM(CASE WHEN decimalLatitude IS NULL THEN 1 ELSE 0 END) AS lat_null,
        SUM(CASE WHEN decimalLongitude IS NULL THEN 1 ELSE 0 END) AS lon_null
    FROM read_csv('{CSV}', delim='\t', header=true, ignore_errors=true)
""").fetchdf()
t1 = time.perf_counter()
total = nulls['total'].iloc[0]
print(f"\n⚠️ Nulidad de campos clave ({t1 - t0:.1f}s):")
for col in nulls.columns:
    if col == 'total':
        continue
    val = nulls[col].iloc[0]
    pct = val / total * 100
    print(f"   {col:25s}: {val:>12,.0f}  ({pct:.1f}%)")

print("\n✅ EDA Overview completado.")
