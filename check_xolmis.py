import duckdb

CSV = "0022205-260226173443078.csv"
con = duckdb.connect()
READ = f"read_csv('{CSV}', delim='\t', header=true, ignore_errors=true)"

# Comprobar la ortografía exacta en el dataset
print("Buscando variaciones de Xolmis pyrope...")
results = con.sql(f"""
    SELECT species, COUNT(*) as count
    FROM {READ}
    WHERE species LIKE 'Xolmis%'
    GROUP BY species
""").df()

print(results)
