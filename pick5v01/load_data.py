import duckdb
import csv
from datetime import datetime

# Connect to DuckDB
conn = duckdb.connect('database/pick5.db')

# Open the CSV file
with open('data/winning_numbers.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Parse the date (mm/dd/yyyy) to yyyy-mm-dd
        try:
            draw_date = datetime.strptime(row['Date'], '%m/%d/%Y').strftime('%Y-%m-%d')
        except ValueError:
            print(f"Invalid date format: {row['Date']}. Skipping row.")
            continue
        
        # Split the Numbers into individual integers
        numbers = row['Numbers'].split()
        if len(numbers) != 5:
            print(f"Skipping row with invalid numbers: {row['Numbers']}")
            continue
        try:
            number1, number2, number3, number4, number5 = map(int, numbers)
        except ValueError:
            print(f"Non-integer values found in numbers: {row['Numbers']}. Skipping row.")
            continue
        
        # Insert into DuckDB
        try:
            conn.execute("""
                INSERT INTO winning_numbers (number1, number2, number3, number4, number5, draw_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (number1, number2, number3, number4, number5, draw_date))
        except duckdb.DuckDBPyConnectionError as e:
            print(f"Error inserting row for date {draw_date}: {e}. Skipping row.")
            continue

# Close the connection
conn.close()

print("Data loaded successfully with 'last_update_date_timestamp'.")

