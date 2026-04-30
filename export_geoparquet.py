"""
Export GeoParquet datasets for QGIS map slides.
Creates proper GeoDataFrames with POINT geometry from lat/lon.
"""
import duckdb
import geopandas as gpd
from shapely.geometry import Point
import time
import os

CSV = "0022205-260226173443078.csv"
PQ = "map_data.parquet"
OUT = "geoparquet"
os.makedirs(OUT, exist_ok=True)

con = duckdb.connect()
READ = f"read_csv('{CSV}', delim='\\t', header=true, ignore_errors=true)"


def to_geoparquet(df, filename, description):
    """Convert a pandas DataFrame with lat/lon to GeoParquet."""
    t0 = time.perf_counter()
    geometry = gpd.points_from_xy(df['lon'], df['lat'])
    gdf = gpd.GeoDataFrame(df.drop(columns=['lat', 'lon']), geometry=geometry, crs="EPSG:4326")
    path = os.path.join(OUT, filename)
    gdf.to_parquet(path)
    size_mb = os.path.getsize(path) / 1024 / 1024
    t1 = time.perf_counter()
    print(f"  ✅ {filename}: {len(gdf):,.0f} rows, {size_mb:.0f} MB ({t1-t0:.1f}s)")
    print(f"     {description}")
    return gdf


# ================================================================
# 1. Slide 2 — Raw (all points, no filter)
# ================================================================
print("\n📦 Slide 2 — Raw (all records with coords)")
df = con.sql(f"""
    SELECT
        decimalLatitude AS lat,
        decimalLongitude AS lon,
        phylum, class, basisOfRecord AS basis,
        occurrenceStatus AS status, year
    FROM {READ}
    WHERE decimalLatitude IS NOT NULL AND decimalLongitude IS NOT NULL
""").fetchdf()
to_geoparquet(df, "slide_02_raw_all.parquet",
              "ALL records with coords, no filter. For 'raw' overview map.")


# ================================================================
# 2. Slide 9 — Filtered, classified by Phylum
# ================================================================
print("\n📦 Slide 9 — Filtered by Phylum")
df = con.sql(f"""
    SELECT
        decimalLatitude AS lat,
        decimalLongitude AS lon,
        phylum, year
    FROM {READ}
    WHERE decimalLatitude IS NOT NULL AND decimalLongitude IS NOT NULL
      AND occurrenceStatus = 'PRESENT'
      AND basisOfRecord != 'FOSSIL_SPECIMEN'
""").fetchdf()
to_geoparquet(df, "slide_09_phylum.parquet",
              "Filtered: PRESENT only, no fossils. Classified by phylum. Nulls: 7,253 (0.03%)")


# ================================================================
# 3. Slide 10 — Filtered, classified by Class
# ================================================================
print("\n📦 Slide 10 — Filtered by Class")
df = con.sql(f"""
    SELECT
        decimalLatitude AS lat,
        decimalLongitude AS lon,
        class, phylum, year
    FROM {READ}
    WHERE decimalLatitude IS NOT NULL AND decimalLongitude IS NOT NULL
      AND occurrenceStatus = 'PRESENT'
      AND basisOfRecord != 'FOSSIL_SPECIMEN'
""").fetchdf()
to_geoparquet(df, "slide_10_class.parquet",
              "Filtered: PRESENT only, no fossils. Classified by class. Nulls: 8.3M (40.3%)")


# ================================================================
# 4. Slide 11 — Filtered, classified by basisOfRecord
# ================================================================
print("\n📦 Slide 11 — Filtered by basisOfRecord")
df = con.sql(f"""
    SELECT
        decimalLatitude AS lat,
        decimalLongitude AS lon,
        basisOfRecord AS basis, year
    FROM {READ}
    WHERE decimalLatitude IS NOT NULL AND decimalLongitude IS NOT NULL
      AND occurrenceStatus = 'PRESENT'
      AND basisOfRecord != 'FOSSIL_SPECIMEN'
""").fetchdf()
to_geoparquet(df, "slide_11_basis.parquet",
              "Filtered: PRESENT only, no fossils. Classified by basisOfRecord. No nulls.")


print("\n✅ All GeoParquet files exported to geoparquet/")
print("   Open in QGIS: Layer > Add Layer > Add Vector Layer > select .parquet file")
