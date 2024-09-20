import duckdb

# Connect to DuckDB (creates 'pick5.db' if it doesn't exist)
conn = duckdb.connect('database/pick5.db')

# Create the 'winning_numbers' table with 'draw_date' as the primary key
conn.execute("""
    CREATE TABLE IF NOT EXISTS winning_numbers (
        number1 INTEGER,
        number2 INTEGER,
        number3 INTEGER,
        number4 INTEGER,
        number5 INTEGER,
        draw_date DATE PRIMARY KEY,
        last_update_date_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Close the connection
conn.close()

print("Table 'winning_numbers' created successfully with 'draw_date' as PRIMARY KEY.")

