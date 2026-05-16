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
    # 1. Fetch all questions from the database
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM questions")
    db_questions = cur.fetchall()
    conn.close()

    # 2. If we receive hero and enemy in the URL via GET, start a NEW game
    if request.method == 'GET' and request.args.get('hero'):
        session['q_no'] = 1
        session['player_hp'] = 100
        session['enemy_hp'] = 100
        session['hero'] = request.args.get('hero')
        session['enemy'] = request.args.get('enemy')

    # Safety catch: redirect if they didn't go through character selection
    if 'q_no' not in session:
        return redirect('/character_select')

    # 3. Handle Answer Submission
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        current_q_index = session['q_no'] - 1

        # Check the answer and adjust HP
        if current_q_index < len(db_questions):
            # In our DB setup, the correct answer is the 7th column (index 6)
            correct_answer = db_questions[current_q_index][6]

            if user_answer == correct_answer:
                session['enemy_hp'] -= 10
            else:
                session['player_hp'] -= 10
            
            # Advance to the next question
            session['q_no'] += 1

    # 4. Check Game Over / Victory / Draw Conditions
    if session['player_hp'] <= 0:
        session.pop('q_no', None) 
        return "<body style='background:black; color:red; text-align:center; font-family:Arial; padding-top:100px;'><h1>Game Over! You lost.</h1><a href='/character_select'><button style='padding:15px 30px; font-size:20px; margin-top:20px; cursor:pointer;'>Play Again</button></a></body>"
    
    if session['enemy_hp'] <= 0:
        session.pop('q_no', None)
        return "<body style='background:black; color:#00f3ff; text-align:center; font-family:Arial; padding-top:100px;'><h1>Victory! You defeated the enemy!</h1><a href='/character_select'><button style='padding:15px 30px; font-size:20px; margin-top:20px; cursor:pointer;'>Play Again</button></a></body>"
    
    if session['q_no'] > len(db_questions):
        session.pop('q_no', None)
        return "<body style='background:black; color:white; text-align:center; font-family:Arial; padding-top:100px;'><h1>It's a Draw! Out of questions.</h1><a href='/character_select'><button style='padding:15px 30px; font-size:20px; margin-top:20px; cursor:pointer;'>Play Again</button></a></body>"

    # 5. Prepare the next question to render
    current_q_index = session['q_no'] - 1
    question_data = db_questions[current_q_index]

    # In our DB setup:
    # question_data[1] = the question text
    # question_data[2] = Option 1
    # question_data[3] = Option 2
    # question_data[4] = Option 3
    # question_data[5] = Option 4
    return render_template(
        'battle_mode.html',
        hero=session['hero'],
        enemy=session['enemy'],
        player_hp=session['player_hp'],
        enemy_hp=session['enemy_hp'],
        q_no=session['q_no'],
        question=question_data[1],
        option1=question_data[2],
        option2=question_data[3],
        option3=question_data[4],
        option4=question_data[5]
    )
    # SURVIVAL MODE
@app.route('/survival_mode', methods=['GET', 'POST'])
def survival_mode():
    # List of enemies to randomly spawn
    ENEMY_LIST = ["thanos", "loki", "ultron", "doctor doom"]

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM questions")
    db_questions = cur.fetchall()
    conn.close()

    # 1. Start of Game Setup
    if request.method == 'GET' and request.args.get('hero'):
        session['surv_wave'] = 1
        session['surv_hp'] = 100
        session['surv_score'] = 0
        session['surv_q_no'] = 1
        session['surv_hero'] = request.args.get('hero')
        session['surv_enemy'] = random.choice(ENEMY_LIST) # Spawn first random enemy

    if 'surv_hp' not in session:
        return redirect('/character_select')

    # 2. Handle Answers
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        current_q_index = session['surv_q_no'] - 1

        if current_q_index < len(db_questions):
            correct_answer = db_questions[current_q_index][6]

            if user_answer == correct_answer:
                # Correct: Defeat enemy, Score +10, Next Wave
                session['surv_wave'] += 1
                session['surv_score'] += 10
                session['surv_enemy'] = random.choice(ENEMY_LIST) # Spawn new enemy!
            else:
                # Wrong: Hero loses 10 HP
                session['surv_hp'] -= 10
            
            session['surv_q_no'] += 1 # Move to next question

    # 3. Check Game Over
    if session['surv_hp'] <= 0:
        final_score = session['surv_score']
        session.pop('surv_hp', None) # Clear game state
        return f"<body style='background:black; color:red; text-align:center; font-family:Arial; padding-top:100px;'><h1>GAME OVER</h1><h2>Final Score: {final_score}</h2><a href='/character_select'><button style='padding:15px 30px; font-size:20px; margin-top:20px; cursor:pointer;'>Play Again</button></a></body>"

    # Check if they survived ALL questions in the database
    if session['surv_q_no'] > len(db_questions):
        final_score = session['surv_score']
        session.pop('surv_hp', None)
        return f"<body style='background:black; color:gold; text-align:center; font-family:Arial; padding-top:100px;'><h1>YOU SURVIVED THEM ALL!</h1><h2>Final Score: {final_score}</h2><a href='/character_select'><button style='padding:15px 30px; font-size:20px; margin-top:20px; cursor:pointer;'>Play Again</button></a></body>"

    # 4. Prepare data for the HTML template
    current_q_index = session['surv_q_no'] - 1
    question_data = db_questions[current_q_index]

    return render_template(
        'survival_mode.html',
        hero=session['surv_hero'],
        enemy=session['surv_enemy'],
        player_hp=session['surv_hp'],
        wave=session['surv_wave'],
        score=session['surv_score'],
        question=question_data[1],
        option1=question_data[2],
        option2=question_data[3],
        option3=question_data[4],
        option4=question_data[5]
    )

# keep this at the END of app.py
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
