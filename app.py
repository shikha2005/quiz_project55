from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__, static_folder='static')
app.secret_key = "secret"

# HOME
@app.route('/')
def home():
    return render_template('index.html')

# LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = u
            session['role'] = user[3]

            if user[3] == 'admin':
                return redirect('/admin')
            else:
                return redirect('/mode')
        else:
            return "Invalid Login"

    return render_template('login.html')

# QUIZ
@app.route('/quiz')
def quiz():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM questions")
    questions = cur.fetchall()
    conn.close()

    return render_template('quiz.html', questions=questions)

# RESULT
@app.route('/result', methods=['POST'])
def result():
    score = 0
    answers = request.form

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM questions")
    questions = cur.fetchall()
    conn.close()

    for q in questions:
        if answers.get(str(q[0])) == q[6]:
            score += 1

    return render_template('result.html', score=score, total=len(questions))

# ADMIN
@app.route('/admin', methods=['GET','POST'])
def admin():
    if session.get('role') != 'admin':
        return "Access Denied"

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':
        q = request.form['question']
        o1 = request.form['o1']
        o2 = request.form['o2']
        o3 = request.form['o3']
        o4 = request.form['o4']
        ans = request.form['answer']

        cur.execute("INSERT INTO questions (question, option1, option2, option3, option4, correct_answer) VALUES (?, ?, ?, ?, ?, ?)", (q,o1,o2,o3,o4,ans))
        conn.commit()

    # 🔥 ADD THIS (VERY IMPORTANT)
    cur.execute("SELECT * FROM questions")
    questions = cur.fetchall()

    conn.close()

    return render_template('admin.html', questions=questions)
@app.route('/delete/<int:id>')
def delete(id):
    if session.get('role') != 'admin':
        return "Access Denied"

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("DELETE FROM questions WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/admin')

  
# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
    #SIGN UP
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        if len(p) < 5:
            return "Password must be at least 5 characters"

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, 'user')",
            (u, p)
        )

        conn.commit()
        conn.close()
        return redirect('/login')

    return render_template('signup.html')
    #edit
@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    if session.get('role') != 'admin':
        return "Access Denied"

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':
        q = request.form['question']
        o1 = request.form['o1']
        o2 = request.form['o2']
        o3 = request.form['o3']
        o4 = request.form['o4']
        ans = request.form['answer']

        cur.execute("""
            UPDATE questions 
            SET question=?, option1=?, option2=?, option3=?, option4=?, correct_answer=? 
            WHERE id=?
        """, (q, o1, o2, o3, o4, ans, id))

        conn.commit()
        conn.close()

        return redirect('/admin')

    # GET request (load existing data)
    cur.execute("SELECT * FROM questions WHERE id=?", (id,))
    question = cur.fetchone()
    conn.close()

    return render_template('edit.html', q=question)
    #mode
# mode page
@app.route('/mode')
def mode():
    return render_template('mode.html')
    #character
@app.route('/character_select')
def character_select():
    return render_template('character_select.html')
    #battle mode
@app.route('/battle_mode')
def battle_mode():

    hero = request.args.get('hero')
    enemy = request.args.get('enemy')

    return render_template(
        'battle_mode.html',
        hero=hero,
        enemy=enemy,
        player_hp=100,
        enemy_hp=100
    )


# keep this at the END of app.py
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
