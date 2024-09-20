import duckdb
from datetime import datetime, timedelta, date
import sys
import random

# Random colors for terminal output
colors = ['\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m']
reset = '\033[0m'

# Fun messages for every interaction!
fun_messages = [
    "Hold on to your seatbelt! We're diving into the database!",
    "Searching for missing dates like Sherlock Holmes, but cooler!",
    "Get ready, we're going on a wild date-finding ride!",
    "Let’s see if your database is as punctual as a Swiss watch!",
    "Woohoo! Time to check if any dates went on vacation!"
]

def random_color():
    """Returns a random terminal color."""
    return random.choice(colors)

def print_fun_message():
    """Prints a random fun message in a random color."""
    print(f"{random_color()}{random.choice(fun_messages)}{reset}")

def get_existing_dates(conn):
    """Fetch all draw_dates from the database and return as a set of date objects."""
    print_fun_message()
    query = "SELECT draw_date FROM winning_numbers"
    result = conn.execute(query).fetchall()
    existing_dates = set()
    for row in result:
        if row[0]:
            existing_dates.add(row[0])
    return existing_dates

def generate_date_range(start_date, end_date):
    """Generate a list of dates from start_date to end_date inclusive."""
    print(f"{random_color()}Generating date range from {start_date} to {end_date}...{reset}")
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]

def find_missing_dates(existing_dates, date_range):
    """Find and return the list of missing dates."""
    print(f"{random_color()}Scanning for missing dates...{reset}")
    return [date for date in date_range if date not in existing_dates]

def main():
    # Define the correct database path
    DATABASE = '/Users/kanduha/pick5v01/database/pick5.db'  # Updated database path

    # Handle command-line argument for start date
    if len(sys.argv) != 2:
        print(f"{random_color()}Oops! Usage: python3 check_missing_dates.py mm/dd/yyyy{reset}")
        sys.exit(1)

    start_date_str = sys.argv[1]

    # Parse the start date
    try:
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y').date()
        print(f"{random_color()}We’ve successfully parsed the start date: {start_date}{reset}")
    except ValueError:
        print(f"{random_color()}Error: Start date must be in mm/dd/yyyy format. Are you testing my patience?{reset}")
        sys.exit(1)

    # Define the end date as yesterday
    today = date.today()
    end_date = today - timedelta(days=1)

    if start_date > end_date:
        print(f"{random_color()}Error: Time travel isn’t allowed! Start date cannot be after yesterday.{reset}")
        sys.exit(1)

    # Connect to DuckDB
    try:
        conn = duckdb.connect(DATABASE)
        print(f"{random_color()}Connection established! Ready for action!{reset}")
    except Exception as e:
        print(f"{random_color()}Database error: {e}. Did the ducks sabotage the connection?{reset}")
        sys.exit(1)

    # Fetch existing dates
    existing_dates = get_existing_dates(conn)

    # Generate the full date range
    full_date_range = generate_date_range(start_date, end_date)

    # Find missing dates
    missing_dates = find_missing_dates(existing_dates, full_date_range)

    # Close the connection
    conn.close()
    print(f"{random_color()}Connection closed. The database is taking a nap.{reset}")

    # Display the results
    if missing_dates:
        print(f"{random_color()}🚨 Missing dates detected between {start_date.strftime('%m/%d/%Y')} and {end_date.strftime('%m/%d/%Y')}: 🚨{reset}")
        for missing_date in missing_dates:
            print(f"{random_color()}{missing_date.strftime('%m/%d/%Y')}{reset}")
        print(f"{random_color()}Time to find those lost dates! Go go go! 🕵️‍♂️{reset}")
    else:
        print(f"{random_color()}🎉 No missing dates found between {start_date.strftime('%m/%d/%Y')} and {end_date.strftime('%m/%d/%Y')}. The database is spotless! 🎉{reset}")

if __name__ == "__main__":
    main()

