from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# create connection to database1
conn = sqlite3.connect('users.db')

c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users
             (uid INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL,
              password TEXT NOT NULL)''')

conn.commit()
conn.close()

# database2
conn2 = sqlite3.connect('client.db')
c2 = conn2.cursor()
c2.execute('''CREATE TABLE IF NOT EXISTS clients
             (cid INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              medicine TEXT NOT NULL,
              medicine_timing DATETIME NOT NULL)''')
conn2.commit()
conn2.close()


@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['username'] = user[1]
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html', error=None)

@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session and session['logged_in']:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect('/login')

@app.route('/addmed', methods=['GET', 'POST'])
def addmed():
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'POST':
            name = session['username']
            medicine = request.form['medicine']
            medicine_timing = request.form['medicine_timing']
            
            conn2 = sqlite3.connect('client.db')
            c2 = conn2.cursor()
            c2.execute('INSERT INTO clients (name, medicine, medicine_timing) VALUES (?, ?, ?)', (name, medicine, medicine_timing))
            conn2.commit()
            conn2.close()
            return redirect('/home')
        else:
            return render_template('addmed.html', username=session['username'])
    else:
        return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        
        session['logged_in'] = True
        session['username'] = username
        
        return redirect('/dashboard')
    else:
        return render_template('register.html')

@app.route('/home')
def home():
    if 'logged_in' in session and session['logged_in']:
        name = session['username']
        conn2 = sqlite3.connect('client.db')
        cursor2 = conn2.cursor()
        cursor2.execute('SELECT name, medicine, medicine_timing FROM clients WHERE name = ?', (name,))
        results = cursor2.fetchall()
        conn2.close()
        return render_template('index.html', results=results, username=session['username'])
    else:
        return redirect('/login')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

app.run(host='0.0.0.0', port=81)
