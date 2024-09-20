import duckdb

# Connect to DuckDB
conn = duckdb.connect('database/pick5.db')

# Query the first few records
df = conn.execute("SELECT * FROM winning_numbers ORDER BY draw_date LIMIT 5").fetchdf()
print(df)

# Close the connection
conn.close()
