"""
Extract map data from the 11GB CSV to Parquet for fast map rendering.
Only extracts columns needed for maps: coords + taxonomy + basisOfRecord + occurrenceStatus.
Filters: with coordinates only.
"""
import duckdb
import time

CSV = "0022205-260226173443078.csv"
con = duckdb.connect()
READ = f"read_csv('{CSV}', delim='\\t', header=true, ignore_errors=true)"

t0 = time.perf_counter()

# Extract to parquet — only columns needed, with coords
con.sql(f"""
    COPY (
        SELECT
            decimalLatitude AS lat,
            decimalLongitude AS lon,
            phylum,
            class,
            basisOfRecord AS basis,
            occurrenceStatus AS status,
            year
        FROM {READ}
        WHERE decimalLatitude IS NOT NULL
          AND decimalLongitude IS NOT NULL
    ) TO 'map_data.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)
""")

t1 = time.perf_counter()

# Check size
import os
size_mb = os.path.getsize('map_data.parquet') / 1024 / 1024
n = con.sql("SELECT COUNT(*) FROM 'map_data.parquet'").fetchone()[0]
print(f"DONE: {n:,.0f} rows, {size_mb:.0f} MB, {t1-t0:.1f}s")
