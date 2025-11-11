from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions

# --- Database setup ---
def init_db():
    conn = sqlite3.connect('bmi.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bmi_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    weight REAL,
                    height REAL,
                    bmi REAL,
                    category TEXT,
                    created_at TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# --- Helper function ---
def get_user_id():
    """Assign a unique ID to each new visitor."""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    user_id = get_user_id()
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
                c.execute('INSERT INTO bmi_history (user_id, weight, height, bmi, category, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                          (user_id, weight, height * 100, bmi, category, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()

        except ValueError:
            message = "Please enter valid numeric values."

    # Fetch only this user's history
    conn = sqlite3.connect('bmi.db')
    c = conn.cursor()
    c.execute('SELECT weight, height, bmi, category, created_at FROM bmi_history WHERE user_id = ? ORDER BY id DESC LIMIT 10', (user_id,))
    history = c.fetchall()
    conn.close()

    return render_template('index.html', bmi=bmi, category=category, message=message, history=history)


@app.route('/clear', methods=['POST'])
def clear_history():
    """Delete this user's records from the database."""
    user_id = get_user_id()
    conn = sqlite3.connect('bmi.db')
    c = conn.cursor()
    c.execute('DELETE FROM bmi_history WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
