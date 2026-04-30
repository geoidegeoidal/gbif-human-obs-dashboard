import geopandas as gpd
import os

files = ["diuca_diuca_human_obs.gpkg", "xolmis_pyrope_human_obs.gpkg"]
target_crs = "EPSG:32719"

for f in files:
    if os.path.exists(f):
        print(f"Reproyectando {f} a {target_crs}...")
        gdf = gpd.read_file(f)
        
        # Reproyectar
        gdf_reprojected = gdf.to_crs(target_crs)
        
        # Guardar con sufijo o sobreescribir? 
        # El usuario pidió "exportalo en epsg 32719 mejor", lo cual sugiere que prefiere este formato.
        # Guardaré uno nuevo con el sufijo _32719 para no borrar el original por si acaso, 
        # pero le avisaré al usuario.
        output_name = f.replace(".gpkg", "_32719.gpkg")
        gdf_reprojected.to_file(output_name, driver="GPKG")
        print(f"✅ Guardado como {output_name}")
    else:
        print(f"⚠️ No se encontró el archivo {f}")
