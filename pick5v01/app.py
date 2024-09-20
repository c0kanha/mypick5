from flask import Flask, render_template, request, redirect, url_for
import duckdb
from datetime import datetime

app = Flask(__name__)

DATABASE = '/Users/kanduha/pick5v01/database/pick5.db'

# Helper function to get the latest winning numbers
def get_latest_winning_numbers(limit=10):
    conn = duckdb.connect(DATABASE)
    query = """
        SELECT draw_date, number1, number2, number3, number4, number5, last_update_date_timestamp
        FROM winning_numbers
        ORDER BY draw_date DESC
        LIMIT ?
    """
    result = conn.execute(query, [limit]).fetchall()
    conn.close()
    return result

# Helper function to validate the date format
def validate_date(date_str):
    """Validates if a date string is in the correct YYYY-MM-DD format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    update_row = None
    if request.method == 'POST' and 'draw_date' in request.form:
        draw_date = request.form.get('draw_date')
        update_row = get_winning_number_by_date(draw_date) if draw_date else None
    
    return render_template('index.html', winning_numbers=get_latest_winning_numbers(), update_row=update_row)

@app.route('/add', methods=['POST'])
def add():
    draw_date = request.form.get('draw_date')
    numbers = request.form.get('numbers')
    
    if not draw_date or not validate_date(draw_date):
        return "Error: Invalid or missing draw date. Please enter a valid date in YYYY-MM-DD format.", 400
    
    if not numbers:
        return "Error: No numbers provided. Please enter valid numbers.", 400
    
    try:
        number1, number2, number3, number4, number5 = map(int, numbers.split())
    except ValueError:
        return "Error: Invalid number format. Please enter five valid space-separated numbers.", 400
    
    conn = duckdb.connect(DATABASE)
    conn.execute("""
        INSERT INTO winning_numbers (draw_date, number1, number2, number3, number4, number5)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (draw_date, number1, number2, number3, number4, number5))
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
def update():
    original_draw_date = request.form.get('original_draw_date')
    new_draw_date = request.form.get('new_draw_date')
    new_numbers = request.form.get('new_numbers')
    
    if not new_draw_date or not validate_date(new_draw_date):
        return "Error: Invalid or missing new draw date. Please enter a valid date in YYYY-MM-DD format.", 400
    
    if not new_numbers:
        return "Error: No numbers provided. Please enter valid numbers.", 400
    
    try:
        number1, number2, number3, number4, number5 = map(int, new_numbers.split())
    except ValueError:
        return "Error: Invalid number format. Please enter five valid space-separated numbers.", 400
    
    conn = duckdb.connect(DATABASE)
    conn.execute("""
        UPDATE winning_numbers
        SET draw_date = ?, number1 = ?, number2 = ?, number3 = ?, number4 = ?, number5 = ?, last_update_date_timestamp = CURRENT_TIMESTAMP
        WHERE draw_date = ?
    """, (new_draw_date, number1, number2, number3, number4, number5, original_draw_date))
    conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

