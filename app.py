from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Initialize DB if it doesn't exist
def init_db():
    if not os.path.exists('wallet.db'):
        with sqlite3.connect('wallet.db') as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    balance REAL DEFAULT 0.0,
                    frozen INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        try:
            with sqlite3.connect('wallet.db') as conn:
                conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
                conn.commit()
                return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            return "Email already registered. <a href='/signup'>Try again</a>"
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    with sqlite3.connect('wallet.db') as conn:
        cur = conn.execute("SELECT id, password FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return redirect(url_for('wallet'))
        return "Invalid credentials. <a href='/'>Try again</a>"

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/wallet')
def wallet():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('wallet.html')

@app.route('/api/wallet', methods=['POST'])
def wallet_api():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']
    data = request.get_json()
    action = data.get('action')
    amount = float(data.get('amount', 0))
    response = {}

    with sqlite3.connect('wallet.db') as conn:
        c = conn.cursor()
        c.execute("SELECT balance, frozen FROM users WHERE id = ?", (user_id,))
        result = c.fetchone()

        if not result:
            return jsonify({"error": "User not found"})

        balance, frozen = result

        if frozen:
            return jsonify({"message": "Account is frozen."})

        if action == 'add':
            balance += amount
        elif action == 'subtract':
            if amount > balance:
                return jsonify({"message": "Insufficient funds."})
            balance -= amount
        elif action == 'reward':
            balance += 10  # fixed reward
        elif action == 'freeze':
            c.execute("UPDATE users SET frozen = 1 WHERE id = ?", (user_id,))
            conn.commit()
            return jsonify({"message": "Account frozen."})
        elif action == 'unfreeze':
            c.execute("UPDATE users SET frozen = 0 WHERE id = ?", (user_id,))
            conn.commit()
            return jsonify({"message": "Account unfrozen."})
        elif action == 'convert':
            usd_balance = round(balance * 0.012, 2)
            return jsonify({"message": f"Balance in USD: ${usd_balance}"})
        elif action == 'check':
            return jsonify({"message": f"Your current balance is ₹{balance}"})

        c.execute("UPDATE users SET balance = ? WHERE id = ?", (balance, user_id))
        conn.commit()
        response['message'] = f"New Balance: ₹{balance}"

    return jsonify(response)
# Temporary: Initialize DB
if not os.path.exists('wallet.db'):
    with app.app_context():
        init_db()

if __name__ == '__main__':
    app.run(debug=True)