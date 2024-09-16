# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import duckdb
from datetime import datetime
from forms import AddWinningNumberForm, EditRecordForm
import os
import random

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_secure_random_key')  # Replace with a secure key in production

# Database path
DB_PATH = os.path.join(os.getcwd(), 'database', 'winning_numbers.duckdb')

def get_db():
    if 'db' not in g:
        g.db = duckdb.connect(database=DB_PATH, read_only=False)
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Ensure the table exists
with app.app_context():
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS winning_numbers (
        date DATE PRIMARY KEY,
        numbers TEXT NOT NULL,
        DB_TMSTAMP TIMESTAMP DEFAULT now()
    )
    """)
    db.commit()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate_random_numbers():
    db = get_db()
    frequency = {}
    all_numbers = db.execute("SELECT numbers FROM winning_numbers").fetchall()
    for record in all_numbers:
        nums = map(int, record[0].split(','))
        for num in nums:
            frequency[num] = frequency.get(num, 0) + 1
    top_five = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    bottom_five = sorted(frequency.items(), key=lambda x: x[1])[:5]
    
    if request.method == 'POST':
        # Step 1: Exclude selected numbers
        excluded_numbers = request.form.getlist('excluded_numbers')
        excluded_numbers = [int(num) for num in excluded_numbers]
        session['excluded_numbers_step1'] = excluded_numbers
        return redirect(url_for('exclude_numbers_step2'))
    
    return render_template('generate_random_numbers.html', top_five=top_five, bottom_five=bottom_five)

@app.route('/generate/step2', methods=['GET', 'POST'])
def exclude_numbers_step2():
    if 'excluded_numbers_step1' not in session:
        return redirect(url_for('generate_random_numbers'))
    
    if request.method == 'POST':
        # Step 2: Exclude numbers from last three draws
        excluded_numbers_step2 = request.form.getlist('excluded_numbers_step2')
        excluded_numbers_step2 = [int(num) for num in excluded_numbers_step2]
        session['excluded_numbers_step2'] = excluded_numbers_step2
        return redirect(url_for('exclude_numbers_step3'))
    
    # Fetch last three draws separated by date
    db = get_db()
    last_three = db.execute("""
        SELECT date, numbers FROM winning_numbers
        ORDER BY date DESC
        LIMIT 3
    """).fetchall()
    last_three_numbers = {}
    for record in last_three:
        date = record[0].strftime('%Y-%m-%d')
        nums = [int(num) for num in record[1].split(',')]
        last_three_numbers[date] = nums
    
    return render_template('exclude_numbers_step2.html', last_three_numbers=last_three_numbers)

@app.route('/generate/step3', methods=['GET', 'POST'])
def exclude_numbers_step3():
    if 'excluded_numbers_step1' not in session or 'excluded_numbers_step2' not in session:
        return redirect(url_for('generate_random_numbers'))
    
    db = get_db()
    frequency = {}
    all_numbers = db.execute("SELECT numbers FROM winning_numbers").fetchall()
    for record in all_numbers:
        nums = map(int, record[0].split(','))
        for num in nums:
            frequency[num] = frequency.get(num, 0) + 1
    top_five = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    bottom_five = sorted(frequency.items(), key=lambda x: x[1])[:5]
    
    if request.method == 'POST':
        # Step 3: Select top N frequent numbers to include
        top_n = int(request.form.get('top_n', 0))
        session['top_n'] = top_n
        return redirect(url_for('generate_random_numbers_result'))
    
    return render_template('exclude_numbers_step3.html', top_five=top_five, bottom_five=bottom_five)

@app.route('/generate/result', methods=['GET'])
def generate_random_numbers_result():
    if 'excluded_numbers_step1' not in session or 'excluded_numbers_step2' not in session or 'top_n' not in session:
        return redirect(url_for('generate_random_numbers'))
    
    excluded = set(session['excluded_numbers_step1'] + session['excluded_numbers_step2'])
    top_n = session['top_n']
    
    # Get top N numbers to include
    db = get_db()
    frequency = {}
    all_numbers = db.execute("SELECT numbers FROM winning_numbers").fetchall()
    for record in all_numbers:
        nums = map(int, record[0].split(','))
        for num in nums:
            frequency[num] = frequency.get(num, 0) + 1
    top_five = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    top_five_numbers = [num for num, freq in top_five]
    selected_top = top_five_numbers[:top_n]
    
    # Get bottom N numbers to include
    bottom_five = sorted(frequency.items(), key=lambda x: x[1])[:5]
    bottom_five_numbers = [num for num, freq in bottom_five]
    
    # Possible numbers are 1-45 excluding the excluded numbers and including selected_top
    possible_numbers = set(range(1, 46)) - excluded
    possible_numbers = list(possible_numbers) + selected_top
    possible_numbers = list(set(possible_numbers))  # Ensure uniqueness
    
    # Generate random numbers, e.g., 5 numbers
    NUM_RANDOM_NUMBERS = 5
    if len(possible_numbers) < NUM_RANDOM_NUMBERS:
        flash(f'Not enough numbers to generate {NUM_RANDOM_NUMBERS} numbers.', 'danger')
        return redirect(url_for('generate_random_numbers'))
    random_numbers = random.sample(possible_numbers, NUM_RANDOM_NUMBERS)
    random_numbers.sort()
    
    # Prepare statistics data
    top_numbers_with_freq = top_five
    bottom_numbers_with_freq = bottom_five
    
    # Clear session
    session.pop('excluded_numbers_step1', None)
    session.pop('excluded_numbers_step2', None)
    session.pop('top_n', None)
    
    return render_template('generate_random_numbers_result.html', 
                           random_numbers=random_numbers,
                           top_numbers=top_numbers_with_freq,
                           bottom_numbers=bottom_numbers_with_freq)

@app.route('/add', methods=['GET', 'POST'])
def add_winning_number():
    form = AddWinningNumberForm()
    if form.validate_on_submit():
        date_input = form.date.data
        numbers_input = form.numbers.data
        try:
            db = get_db()
            db.execute("""
                INSERT INTO winning_numbers (date, numbers)
                VALUES (?, ?)
                ON CONFLICT(date) DO UPDATE SET numbers = excluded.numbers, DB_TMSTAMP = now()
            """, (date_input, numbers_input))
            db.commit()
            flash('Winning numbers added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Error adding winning numbers: {e}', 'danger')
    return render_template('add_winning_number.html', form=form)

@app.route('/history')
def winning_numbers_history():
    db = get_db()
    results = db.execute("""
        SELECT date, numbers FROM winning_numbers
        ORDER BY date DESC
    """).fetchall()
    return render_template('winning_numbers_history.html', records=results)

@app.route('/update', methods=['GET'])
def update_records():
    db = get_db()
    records = db.execute("""
        SELECT * FROM winning_numbers
        ORDER BY DB_TMSTAMP DESC, date DESC
        LIMIT 10
    """).fetchall()
    return render_template('update_records.html', records=records)

@app.route('/edit/<record_date>', methods=['GET', 'POST'])
def edit_record(record_date):
    form = EditRecordForm()
    if request.method == 'GET':
        db = get_db()
        record = db.execute("SELECT * FROM winning_numbers WHERE date = ?", (record_date,)).fetchone()
        if record:
            form.date.data = record[0]
            form.numbers.data = record[1]
        else:
            flash('Record not found.', 'danger')
            return redirect(url_for('update_records'))
    if form.validate_on_submit():
        new_numbers = form.numbers.data
        try:
            db = get_db()
            db.execute("""
                UPDATE winning_numbers
                SET numbers = ?, DB_TMSTAMP = now()
                WHERE date = ?
            """, (new_numbers, form.date.data))
            db.commit()
            flash('Record updated successfully!', 'success')
            return redirect(url_for('update_confirmation', record_date=form.date.data))
        except Exception as e:
            flash(f'Error updating record: {e}', 'danger')
    return render_template('edit_record.html', form=form)

@app.route('/update_confirmation/<record_date>')
def update_confirmation(record_date):
    db = get_db()
    record = db.execute("""
        SELECT date, numbers, DB_TMSTAMP FROM winning_numbers
        WHERE date = ?
    """, (record_date,)).fetchone()
    return render_template('update_confirmation.html', record=record)

# Statistics Routes
@app.route('/stats')
def stats():
    return render_template('statistics.html')

@app.route('/most_frequent')
def most_frequent():
    db = get_db()
    frequency = {}
    all_numbers = db.execute("SELECT numbers FROM winning_numbers").fetchall()
    for record in all_numbers:
        nums = map(int, record[0].split(','))
        for num in nums:
            frequency[num] = frequency.get(num, 0) + 1
    top_numbers = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return render_template('most_frequent.html', top_numbers=top_numbers)

@app.route('/least_frequent')
def least_frequent():
    db = get_db()
    frequency = {}
    all_numbers = db.execute("SELECT numbers FROM winning_numbers").fetchall()
    for record in all_numbers:
        nums = map(int, record[0].split(','))
        for num in nums:
            frequency[num] = frequency.get(num, 0) + 1
    least_numbers = sorted(frequency.items(), key=lambda x: x[1])[:5]
    
    return render_template('least_frequent.html', least_numbers=least_numbers)

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Run the app
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)