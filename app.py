from flask import Flask, render_template, request, redirect, session
import pymysql  # Replaced sqlite3
import os
import random
import time

app = Flask(__name__, static_folder='static')
# Uses Render's environment variable for security, or defaults to "secret"
app.secret_key = os.environ.get("SECRET_KEY", "secret")

# --- HELPER FUNCTION: Securely connects to TiDB Cloud ---
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "YOUR_TIDB_HOST_URL"),
        user=os.environ.get("DB_USER", "YOUR_TIDB_USER"),
        password=os.environ.get("DB_PASSWORD", "YOUR_TIDB_PASSWORD"),
        database=os.environ.get("DB_NAME", "marvel_quiz"),
        port=int(os.environ.get("DB_PORT", 4000)), # TiDB port!
        ssl_verify_cert=True,
        ssl_verify_identity=True
    )

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

        conn = get_db_connection()
        cur = conn.cursor()
        # Note: Changed ? to %s for MySQL syntax
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (u, p))
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

    conn = get_db_connection()
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

    conn = get_db_connection()
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

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        q = request.form['question']
        o1 = request.form['o1']
        o2 = request.form['o2']
        o3 = request.form['o3']
        o4 = request.form['o4']
        ans = request.form['answer']

        # Note: Changed ? to %s
        cur.execute("INSERT INTO questions (question, option1, option2, option3, option4, correct_answer) VALUES (%s, %s, %s, %s, %s, %s)", (q,o1,o2,o3,o4,ans))
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

    conn = get_db_connection()
    cur = conn.cursor()
    # Note: Changed ? to %s
    cur.execute("DELETE FROM questions WHERE id=%s", (id,))
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

        conn = get_db_connection()
        cur = conn.cursor()
        # Note: Changed ? to %s
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, 'user')",
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

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        q = request.form['question']
        o1 = request.form['o1']
        o2 = request.form['o2']
        o3 = request.form['o3']
        o4 = request.form['o4']
        ans = request.form['answer']

        # Note: Changed ? to %s
        cur.execute("""
            UPDATE questions 
            SET question=%s, option1=%s, option2=%s, option3=%s, option4=%s, correct_answer=%s 
            WHERE id=%s
        """, (q, o1, o2, o3, o4, ans, id))

        conn.commit()
        conn.close()
        return redirect('/admin')

    # GET request (load existing data)
    # Note: Changed ? to %s
    cur.execute("SELECT * FROM questions WHERE id=%s", (id,))
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
    game_mode = request.args.get('mode', 'battle') 
    return render_template('character_select.html', mode=game_mode)

# BATTLE MODE
@app.route('/battle_mode', methods=['GET', 'POST'])
def battle_mode():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM battle_questions")
    db_questions = cur.fetchall()
    conn.close()

    if request.method == 'GET' and request.args.get('hero'):
        session['q_no'] = 1
        session['player_hp'] = 100
        session['enemy_hp'] = 100
        session['hero'] = request.args.get('hero')
        session['enemy'] = request.args.get('enemy')

    if 'q_no' not in session:
        return redirect('/character_select')

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        current_q_index = session['q_no'] - 1

        if current_q_index < len(db_questions):
            correct_answer = db_questions[current_q_index][6]

            if user_answer == correct_answer:
                session['enemy_hp'] -= 10
            else:
                session['player_hp'] -= 10
            
            session['q_no'] += 1

    if session['enemy_hp'] <= 0:
        session.pop('q_no', None)
        return """
        <body style='background:#050a15; color:#00f3ff; text-align:center; font-family:Arial; padding-top:100px;'>
            <h1 style='font-size: 50px; text-shadow: 0 0 20px #00f3ff;'>VICTORY! You defeated the enemy!</h1>
            <div style='margin-top: 40px;'>
                <a href='/character_select?mode=battle'><button style='padding:15px 30px; font-size:18px; cursor:pointer; background:transparent; color:white; border:2px solid cyan; border-radius:8px; margin: 10px; transition: 0.3s;'>↻ Play Again</button></a>
                <a href='/'><button style='padding:15px 30px; font-size:18px; cursor:pointer; background:transparent; color:white; border:2px solid #ff003c; border-radius:8px; margin: 10px; transition: 0.3s;'>🏠 Change Mode</button></a>
            </div>
        </body>
        """
    
    elif session['player_hp'] <= 0:
        session.pop('q_no', None) 
        return """
        <body style='background:#050a15; color:#ff003c; text-align:center; font-family:Arial; padding-top:100px;'>
            <h1 style='font-size: 50px; text-shadow: 0 0 20px #ff003c;'>GAME OVER! You lost.</h1>
            <div style='margin-top: 40px;'>
                <a href='/character_select?mode=battle'><button style='padding:15px 30px; font-size:18px; cursor:pointer; background:transparent; color:white; border:2px solid cyan; border-radius:8px; margin: 10px; transition: 0.3s;'>↻ Play Again</button></a>
                <a href='/'><button style='padding:15px 30px; font-size:18px; cursor:pointer; background:transparent; color:white; border:2px solid #ff003c; border-radius:8px; margin: 10px; transition: 0.3s;'>🏠 Change Mode</button></a>
            </div>
        </body>
        """
    
    elif session['q_no'] > len(db_questions):
        session.pop('q_no', None)
        return """
        <body style='background:#050a15; color:white; text-align:center; font-family:Arial; padding-top:100px;'>
            <h1 style='font-size: 50px; text-shadow: 0 0 20px white;'>IT'S A DRAW! Out of questions.</h1>
            <div style='margin-top: 40px;'>
                <a href='/character_select?mode=battle'><button style='padding:15px 30px; font-size:18px; cursor:pointer; background:transparent; color:white; border:2px solid cyan; border-radius:8px; margin: 10px; transition: 0.3s;'>↻ Play Again</button></a>
                <a href='/'><button style='padding:15px 30px; font-size:18px; cursor:pointer; background:transparent; color:white; border:2px solid #ff003c; border-radius:8px; margin: 10px; transition: 0.3s;'>🏠 Change Mode</button></a>
            </div>
        </body>
        """

    current_q_index = session['q_no'] - 1
    question_data = db_questions[current_q_index]

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
    ENEMY_LIST = ["thanos", "loki", "ultron", "doctor doom"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM survival_questions")
    db_questions = cur.fetchall()
    conn.close()

    if request.method == 'GET' and request.args.get('hero'):
        session['surv_wave'] = 1
        session['surv_hp'] = 100
        session['surv_score'] = 0
        session['surv_q_no'] = 1
        session['surv_hero'] = request.args.get('hero')
        session['surv_enemy'] = random.choice(ENEMY_LIST)

    if 'surv_hp' not in session:
        return redirect('/character_select')

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        current_q_index = session['surv_q_no'] - 1

        if current_q_index < len(db_questions):
            correct_answer = db_questions[current_q_index][6]

            if user_answer == correct_answer:
                session['surv_wave'] += 1
                session['surv_score'] += 10
                session['surv_enemy'] = random.choice(ENEMY_LIST)
            else:
                session['surv_hp'] -= 10
            
            session['surv_q_no'] += 1

    if session['surv_hp'] <= 0:
        final_score = session['surv_score']
        session.pop('surv_hp', None) 
        return f"""
        <body style='background:#050a15; color:#ff003c; text-align:center; font-family:Arial; padding-top:100px;'>
            <h1 style='font-size: 50px; text-shadow: 0 0 20px #ff003c;'>GAME OVER</h1>
            <h2 style='color: gold;'>Final Score: {final_score}</h2>
            <div style='margin-top: 40px;'>
                <a href='/character_select?mode=survival'><button style='padding:15px 30px; font-size:18px; cursor:pointer; background:transparent; color:white; border:2px solid cyan; border-radius:8px; margin: 10px;'>↻ Play Again</button></a>
                <a href='/'><button style='padding:15px 30px; font-size:18px; cursor:pointer; background:transparent; color:white; border:2px solid #ff003c; border-radius:8px; margin: 10px;'>🏠 Change Mode</button></a>
            </div>
        </body>
        """

    if session['surv_q_no'] > len(db_questions):
        final_score = session['surv_score']
        session.pop('surv_hp', None)
        return f"""
        <body style='background:#050a15; color:gold; text-align:center; font-family:Arial; padding-top:100px;'>
            <h1 style='font-size: 50px; text-shadow: 0 0 20px gold;'>YOU SURVIVED THEM ALL!</h1>
            <h2>Final Score: {final_score}</h2>
            <div style='margin-top: 40px;'>
                <a href='/character_select?mode=survival'><button style='padding:15px 30px; font-size:18px; cursor:pointer; background:transparent; color:white; border:2px solid cyan; border-radius:8px; margin: 10px;'>↻ Play Again</button></a>
                <a href='/'><button style='padding:15px 30px; font-size:18px; cursor:pointer; background:transparent; color:white; border:2px solid #ff003c; border-radius:8px; margin: 10px;'>🏠 Change Mode</button></a>
            </div>
        </body>
        """

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

# TIME ATTACK MODE
@app.route('/time_attack_mode', methods=['GET', 'POST'])
def time_attack_mode():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM time_attack_questions")
    db_questions = cur.fetchall()
    conn.close()

    if request.method == 'GET' and request.args.get('hero'):
        session['ta_score'] = 0
        session['ta_q_no'] = 1
        session['ta_hero'] = request.args.get('hero')
        session['ta_end_time'] = time.time() + 60 

    if 'ta_end_time' not in session:
        return redirect('/character_select')

    time_left = int(session['ta_end_time'] - time.time())

    if time_left <= 0:
        final_score = session.get('ta_score', 0)
        session.pop('ta_end_time', None) 

        if final_score < 30:
            rank_message = "FAILED! Too slow."
            rank_color = "#ff003c" 
        elif final_score < 70:
            rank_message = "PASSED! Good speed."
            rank_color = "#00f3ff" 
        else:
            rank_message = "S-RANK! Absolute Legend!"
            rank_color = "gold"    
            
        return f"""
        <body style='background:#050a15; color:{rank_color}; text-align:center; font-family:Arial; padding-top:100px;'>
            <h1 style='font-size: 50px; text-shadow: 0 0 20px {rank_color};'>⏱ TIME UP!</h1>
            <h2 style='font-size: 40px;'>{rank_message}</h2>
            <h3 style='color: white; font-size: 30px;'>Final Score: <span style='color: gold;'>{final_score}</span></h3>
            <div style='margin-top: 40px;'>
                <a href='/character_select?mode=time_attack'><button style='padding:15px 30px; font-size:18px; cursor:pointer; background:transparent; color:white; border:2px solid cyan; border-radius:8px; margin: 10px; transition: 0.3s;'>↻ Play Again</button></a>
                <a href='/'><button style='padding:15px 30px; font-size:18px; cursor:pointer; background:transparent; color:white; border:2px solid #ff003c; border-radius:8px; margin: 10px; transition: 0.3s;'>🏠 Change Mode</button></a>
            </div>
        </body>
        """

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        current_q_index = (session['ta_q_no'] - 1) % len(db_questions)
        correct_answer = db_questions[current_q_index][6]

        if user_answer == correct_answer:
            session['ta_score'] += 10 

        session['ta_q_no'] += 1 
        
        time_left = int(session['ta_end_time'] - time.time())
        if time_left <= 0:
            return redirect('/time_attack_mode') 

    current_q_index = (session['ta_q_no'] - 1) % len(db_questions)
    question_data = db_questions[current_q_index]

    return render_template(
        'time_attack_mode.html',
        hero=session['ta_hero'],
        score=session['ta_score'],
        time_left=time_left,
        question=question_data[1],
        option1=question_data[2],
        option2=question_data[3],
        option3=question_data[4],
        option4=question_data[5]
    )

if __name__ == '__main__':
    # This port runs your Flask web app. Keep this as os.environ.get("PORT", 5000) for Render!
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
