import duckdb
from datetime import datetime, timedelta, date
import sys

def get_existing_dates(conn):
    """Fetch all draw_dates from the database and return as a set of date objects."""
    query = "SELECT draw_date FROM winning_numbers"
    result = conn.execute(query).fetchall()
    existing_dates = set()
    for row in result:
        if row[0]:
            existing_dates.add(row[0])
    return existing_dates

def generate_date_range(start_date, end_date):
    """Generate a list of dates from start_date to end_date inclusive."""
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]

def find_missing_dates(existing_dates, date_range):
    """Find and return the list of missing dates."""
    return [date for date in date_range if date not in existing_dates]

def main():
    # Define the correct database path
    DATABASE = '/Users/kanduha/pick5v01/database/pick5.db'  # Updated database path

    # Handle command-line argument for start date
    if len(sys.argv) != 2:
        print("Usage: python3 check_missing_dates.py mm/dd/yyyy")
        sys.exit(1)

    start_date_str = sys.argv[1]

    # Parse the start date
    try:
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y').date()
    except ValueError:
        print("Error: Start date must be in mm/dd/yyyy format.")
        sys.exit(1)

    # Define the end date as yesterday
    today = date.today()
    end_date = today - timedelta(days=1)

    if start_date > end_date:
        print("Error: Start date cannot be after yesterday.")
        sys.exit(1)

    # Connect to DuckDB
    try:
        conn = duckdb.connect(DATABASE)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

    # Fetch existing dates
    existing_dates = get_existing_dates(conn)

    # Generate the full date range
    full_date_range = generate_date_range(start_date, end_date)

    # Find missing dates
    missing_dates = find_missing_dates(existing_dates, full_date_range)

    # Close the connection
    conn.close()

    # Display the results
    if missing_dates:
        print(f"Missing dates between {start_date.strftime('%m/%d/%Y')} and {end_date.strftime('%m/%d/%Y')}:")
        for missing_date in missing_dates:
            print(missing_date.strftime('%m/%d/%Y'))
    else:
        print(f"No missing dates between {start_date.strftime('%m/%d/%Y')} and {end_date.strftime('%m/%d/%Y')}.")

if __name__ == "__main__":
    main()

