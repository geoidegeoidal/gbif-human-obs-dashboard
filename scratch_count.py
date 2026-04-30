import duckdb

CSV = "0022205-260226173443078.csv"
con = duckdb.connect()
READ = f"read_csv('{CSV}', delim='\t', header=true, ignore_errors=true)"

count = con.sql(f"""
    SELECT COUNT(*) 
    FROM {READ} 
    WHERE species = 'Diuca diuca' 
      AND basisOfRecord = 'HUMAN_OBSERVATION'
      AND decimalLatitude IS NOT NULL
      AND decimalLongitude IS NOT NULL
""").fetchone()[0]

print(f"Total records of Diuca diuca by humans: {count}")
