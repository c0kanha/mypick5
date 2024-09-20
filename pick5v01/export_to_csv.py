import duckdb
import csv
from datetime import datetime

def export_winning_numbers_to_csv(db_path, output_csv_path):
    try:
        # Connect to DuckDB
        conn = duckdb.connect(db_path)
        
        # Query to retrieve all data from the winning_numbers table
        query = """
        SELECT draw_date, number1, number2, number3, number4, number5
        FROM winning_numbers
        ORDER BY draw_date
        """
        
        # Fetch data from the table
        result = conn.execute(query).fetchall()
        
        # Open the CSV file for writing
        with open(output_csv_path, 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Numbers']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write each row to CSV in the desired format
            for row in result:
                draw_date = row[0].strftime('%m/%d/%Y')  # Format date as mm/dd/yyyy
                numbers = f"{row[1]:02d} {row[2]:02d} {row[3]:02d} {row[4]:02d} {row[5]:02d}"
                
                writer.writerow({'Date': draw_date, 'Numbers': numbers})
        
        print(f"Data successfully exported to {output_csv_path}.")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Close the DuckDB connection
        conn.close()

if __name__ == "__main__":
    # Path to your DuckDB database
    db_path = '/Users/kanduha/pick5v01/database/pick5.db'
    
    # Path where the CSV file will be saved
    output_csv_path = '/Users/kanduha/pick5v01/data/exported_winning_numbers.csv'
    
    # Export data to CSV
    export_winning_numbers_to_csv(db_path, output_csv_path)

