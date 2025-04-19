from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secretkey'

# Setup DB
def init_db():
    conn = sqlite3.connect('voters.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS voters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id TEXT UNIQUE,
            has_voted INTEGER,
            vote TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        voter_id = request.form['voter_id']
        candidate = request.form.get('candidate')

        conn = sqlite3.connect('voters.db')
        c = conn.cursor()
        c.execute('SELECT has_voted FROM voters WHERE voter_id = ?', (voter_id,))
        result = c.fetchone()

        if result is None:
            c.execute('INSERT INTO voters (voter_id, has_voted, vote) VALUES (?, ?, ?)',
                      (voter_id, 1, candidate))
        elif result[0] == 1:
            return 'You have already voted.'
        else:
            c.execute('UPDATE voters SET has_voted = 1, vote = ? WHERE voter_id = ?', (candidate, voter_id))

        conn.commit()
        conn.close()

        return render_template('success.html', candidate=candidate)

    return render_template('vote.html')

@app.route('/admin')
def admin():
    conn = sqlite3.connect('voters.db')
    c = conn.cursor()
    c.execute('SELECT vote, COUNT(*) FROM voters GROUP BY vote')
    results = c.fetchall()
    conn.close()
    return render_template('admin.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
