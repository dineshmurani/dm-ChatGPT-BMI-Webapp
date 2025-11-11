from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# --- Database setup ---
def init_db():
    conn = sqlite3.connect('bmi.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bmi_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    weight REAL,
                    height REAL,
                    bmi REAL,
                    category TEXT,
                    created_at TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    bmi = None
    category = None
    message = None

    if request.method == 'POST' and 'calculate' in request.form:
        try:
            weight = float(request.form['weight'])
            height = float(request.form['height']) / 100  # convert cm to meters

            if height <= 0:
                message = "Height must be greater than zero."
            else:
                bmi = round(weight / (height ** 2), 2)

                if bmi < 18.5:
                    category = "Underweight"
                elif 18.5 <= bmi < 24.9:
                    category = "Normal weight"
                elif 25 <= bmi < 29.9:
                    category = "Overweight"
                else:
                    category = "Obese"

                # Save to database
                conn = sqlite3.connect('bmi.db')
                c = conn.cursor()
                c.execute('INSERT INTO bmi_history (weight, height, bmi, category, created_at) VALUES (?, ?, ?, ?, ?)',
                          (weight, height * 100, bmi, category, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()

        except ValueError:
            message = "Please enter valid numeric values."

    # Fetch history
    conn = sqlite3.connect('bmi.db')
    c = conn.cursor()
    c.execute('SELECT weight, height, bmi, category, created_at FROM bmi_history ORDER BY id DESC LIMIT 10')
    history = c.fetchall()
    conn.close()

    return render_template('index.html', bmi=bmi, category=category, message=message, history=history)


@app.route('/clear', methods=['POST'])
def clear_history():
    """Delete all records from the database."""
    conn = sqlite3.connect('bmi.db')
    c = conn.cursor()
    c.execute('DELETE FROM bmi_history')
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
