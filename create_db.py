import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

# Questions table
cur.execute('''
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    option4 TEXT,
    correct_answer TEXT
)
''')

# Users table
cur.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT
)
''')

# Insert admin
cur.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")

# Insert 15 questions
questions = [
("What is Python?", "Programming Language", "Snake", "Game", "Car", "1"),
("Capital of India?", "Mumbai", "Delhi", "Kolkata", "Chennai", "2"),
("2 + 2 = ?", "3", "4", "5", "6", "2"),
("Which is a database?", "MySQL", "HTML", "CSS", "JS", "1"),
("Full form of CPU?", "Central Process Unit", "Central Processing Unit", "Computer Processing Unit", "Control Unit", "2"),
("Which language is used for web?", "HTML", "Python", "C++", "Java", "1"),
("Which is input device?", "Keyboard", "Monitor", "Printer", "Speaker", "1"),
("Which is output device?", "Mouse", "Keyboard", "Monitor", "Scanner", "3"),
("Which is OS?", "Windows", "Google", "CPU", "RAM", "1"),
("Which is not programming language?", "Python", "Java", "HTML", "C++", "3"),
("5 * 6 = ?", "30", "20", "25", "35", "1"),
("Which is cloud platform?", "AWS", "MS Word", "Excel", "Notepad", "1"),
("Which is AI example?", "Chatbot", "Calculator", "Mouse", "Keyboard", "1"),
("Which is storage device?", "Hard Disk", "CPU", "Monitor", "Keyboard", "1"),
("Which is mobile OS?", "Android", "Intel", "Oracle", "Python", "1")
]

cur.executemany("INSERT INTO questions (question, option1, option2, option3, option4, correct_answer) VALUES (?, ?, ?, ?, ?, ?)", questions)

conn.commit()
conn.close()

print("Database Ready!")