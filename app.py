from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__, static_folder='static')
app.secret_key = "secret"

# --- 10 CLOUD COMPUTING QUESTIONS FOR BATTLE MODE ---
CLOUD_QUESTIONS = [
    {
        "q": "Which computing model combines multiple computers to solve one task?",
        "options": {"A": "Database Computing", "B": "Parallel Computing", "C": "Word Computing", "D": "Mobile Computing"},
        "answer": "B"
    },
    {
        "q": "Cloud computing has how many essential characteristics?",
        "options": {"A": "2", "B": "3", "C": "5", "D": "7"},
        "answer": "C"
    },
    {
        "q": "Which is NOT a cloud deployment model?",
        "options": {"A": "Private Cloud", "B": "Hybrid Cloud", "C": "Community Cloud", "D": "Binary Cloud"},
        "answer": "D"
    },
    {
        "q": "What does IaaS stand for?",
        "options": {"A": "Internet as a Service", "B": "Infrastructure as a Service", "C": "Internal as a Service", "D": "Information as a Service"},
        "answer": "B"
    },
    {
        "q": "Which company developed VMware?",
        "options": {"A": "Google", "B": "VMware", "C": "Facebook", "D": "Oracle"},
        "answer": "B"
    },
    {
        "q": "Which virtualization uses a hypervisor?",
        "options": {"A": "Full Virtualization", "B": "Mobile Computing", "C": "Nano Computing", "D": "Optical Computing"},
        "answer": "A"
    },
    {
        "q": "Which is a cloud platform by Google?",
        "options": {"A": "Google App Engine", "B": "Google Paint", "C": "Google Docs", "D": "Google Search"},
        "answer": "A"
    },
    {
        "q": "Web 3.0 focuses on:",
        "options": {"A": "Semantic Web", "B": "CDs", "C": "Printers", "D": "Mouse"},
        "answer": "A"
    },
    {
        "q": "Which service is provided by Amazon?",
        "options": {"A": "Amazon EC2", "B": "Amazon Word", "C": "Amazon Paint", "D": "Amazon DOS"},
        "answer": "A"
    },
    {
        "q": "What is the brain of virtualization?",
        "options": {"A": "Firewall", "B": "Hypervisor", "C": "Router", "D": "Browser"},
        "answer": "B"
    }
]

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

    # Fetch all questions
    cur.execute("SELECT * FROM questions")
    questions = cur.fetchall()
    conn.close()

    return render_template('admin.html', questions=questions)

# DELETE
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

# SIGN UP
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

# EDIT
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

# MODE PAGE
@app.route('/mode')
def mode():
    return render_template('mode.html')

# CHARACTER SELECT
@app.route('/character_select')
def character_select():
    return render_template('character_select.html')

# BATTLE MODE
@app.route('/battle_mode', methods=['GET', 'POST'])
def battle_mode():
    # 1. If we receive hero and enemy in the URL via GET, it means a NEW game is starting from the character select screen.
    if request.method == 'GET' and request.args.get('hero'):
        session['q_no'] = 1
        session['player_hp'] = 100
        session['enemy_hp'] = 100
        session['hero'] = request.args.get('hero')
        session['enemy'] = request.args.get('enemy')

    # Safety catch: if they try to access this page directly without going through character selection
    if 'q_no' not in session:
        return redirect('/character_select')

    # 2. Handle Answer Submission
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        current_q_index = session['q_no'] - 1

        # Check the answer and adjust HP
        if current_q_index < len(CLOUD_QUESTIONS):
            correct_answer = CLOUD_QUESTIONS[current_q_index]['answer']

            if user_answer == correct_answer:
                session['enemy_hp'] -= 20
            else:
                session['player_hp'] -= 20
            
            # Advance to the next question
            session['q_no'] += 1

    # 3. Check Game Over / Victory Conditions (Inline basic HTML so you don't need extra templates yet)
    if session['player_hp'] <= 0:
        session.pop('q_no', None) # Clear battle state
        return "<body style='background:black; color:red; text-align:center; font-family:Arial; padding-top:100px;'><h1>Game Over! You lost.</h1><a href='/character_select'><button style='padding:15px 30px; font-size:20px; margin-top:20px; cursor:pointer;'>Play Again</button></a></body>"
    
    if session['enemy_hp'] <= 0:
        session.pop('q_no', None)
        return "<body style='background:black; color:#00f3ff; text-align:center; font-family:Arial; padding-top:100px;'><h1>Victory! You defeated the enemy!</h1><a href='/character_select'><button style='padding:15px 30px; font-size:20px; margin-top:20px; cursor:pointer;'>Play Again</button></a></body>"
    
    if session['q_no'] > len(CLOUD_QUESTIONS):
        session.pop('q_no', None)
        return "<body style='background:black; color:white; text-align:center; font-family:Arial; padding-top:100px;'><h1>It's a Draw! Out of questions.</h1><a href='/character_select'><button style='padding:15px 30px; font-size:20px; margin-top:20px; cursor:pointer;'>Play Again</button></a></body>"

    # 4. Prepare the next question to render
    current_q_index = session['q_no'] - 1
    question_data = CLOUD_QUESTIONS[current_q_index]

    return render_template(
        'battle_mode.html',
        hero=session['hero'],
        enemy=session['enemy'],
        player_hp=session['player_hp'],
        enemy_hp=session['enemy_hp'],
        q_no=session['q_no'],
        question=question_data['q'],
        option1=question_data['options']['A'],
        option2=question_data['options']['B'],
        option3=question_data['options']['C'],
        option4=question_data['options']['D']
    )

# keep this at the END of app.py
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
