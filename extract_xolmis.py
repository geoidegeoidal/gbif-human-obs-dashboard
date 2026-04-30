import duckdb
import geopandas as gpd

CSV = "0022205-260226173443078.csv"
con = duckdb.connect()
READ = f"read_csv('{CSV}', delim='\t', header=true, ignore_errors=true)"

print("Ejecutando la consulta en DuckDB para Xolmis pyrope...")
df = con.sql(f"""
    SELECT *
    FROM {READ} 
    WHERE species = 'Xolmis pyrope' 
      AND basisOfRecord = 'HUMAN_OBSERVATION'
      AND decimalLatitude IS NOT NULL
      AND decimalLongitude IS NOT NULL
""").df()

print(f"Se cargaron {len(df)} registros. Convirtiendo a GeoDataFrame...")

# Crear la geometría e instanciar el GeoDataFrame con sistema de coordenadas WGS84 (EPSG:4326)
gdf = gpd.GeoDataFrame(
    df, 
    geometry=gpd.points_from_xy(df.decimalLongitude, df.decimalLatitude),
    crs="EPSG:4326"
)

# Geopackage tiene problemas con celdas de fecha u objetos con valores mixtos (NA), 
# por precaución vamos a asegurar que todo lo que no sea numerico se guarde como string 
for col in gdf.columns:
    if col != 'geometry':
        if gdf[col].dtype == 'datetime64[ns]':
            gdf[col] = gdf[col].dt.strftime('%Y-%m-%d %H:%M:%S')

output_file = "xolmis_pyrope_human_obs.gpkg"
print(f"Guardando {output_file}...")
gdf.to_file(output_file, driver="GPKG")
print("¡Archivo GeoPackage exportado exitosamente!")
