import sqlite3

# Connect to the database
conn = sqlite3.connect('database.db')
cur = conn.cursor()

# Wipe the slate clean
cur.execute('DROP TABLE IF EXISTS questions') # Drop the old shared table
cur.execute('DROP TABLE IF EXISTS battle_questions')
cur.execute('DROP TABLE IF EXISTS survival_questions')
cur.execute('DROP TABLE IF EXISTS users')

# 1. Create Battle Mode Table
cur.execute('''
CREATE TABLE battle_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT, option1 TEXT, option2 TEXT, option3 TEXT, option4 TEXT, correct_answer TEXT
)
''')

# 2. Create Survival Mode Table
cur.execute('''
CREATE TABLE survival_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT, option1 TEXT, option2 TEXT, option3 TEXT, option4 TEXT, correct_answer TEXT
)
''')

# 3. Create Users Table
cur.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT, password TEXT, role TEXT
)
''')
cur.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")

# --- DATA INSERTION ---

# Battle Mode Questions (Cloud Computing)
cloud_questions = [
    ("Which computing model combines multiple computers to solve one task?", "Database Computing", "Parallel Computing", "Word Computing", "Mobile Computing", "B"),
    ("Cloud computing has how many essential characteristics?", "2", "3", "5", "7", "C"),
    ("Which is NOT a cloud deployment model?", "Private Cloud", "Hybrid Cloud", "Community Cloud", "Binary Cloud", "D"),
    ("What does IaaS stand for?", "Internet as a Service", "Infrastructure as a Service", "Internal as a Service", "Information as a Service", "B"),
    ("Which company developed VMware?", "Google", "VMware", "Facebook", "Oracle", "B"),
    ("Which virtualization uses a hypervisor?", "Full Virtualization", "Mobile Computing", "Nano Computing", "Optical Computing", "A"),
    ("Which is a cloud platform by Google?", "Google App Engine", "Google Paint", "Google Docs", "Google Search", "A"),
    ("Web 3.0 focuses on:", "Semantic Web", "CDs", "Printers", "Mouse", "A"),
    ("Which service is provided by Amazon?", "Amazon EC2", "Amazon Word", "Amazon Paint", "Amazon DOS", "A"),
    ("What is the brain of virtualization?", "Firewall", "Hypervisor", "Router", "Browser", "B")
]

# Survival Mode Questions (VBA)
vba_questions = [
    ("Which window in the Microsoft Excel VBA editor is mainly used to execute statements instantly for testing?", "Properties Window", "Immediate Window", "Project Explorer", "Object Browser", "B"),
    ("Which statement is best for checking multiple conditions in VBA instead of using many If...ElseIf statements?", "For Next", "Select Case", "Do While", "With", "B"),
    ("Which keyword is used to declare a constant value in VBA?", "Dim", "Const", "Static", "Set", "B"),
    ("To get the number of characters in a string in VBA, which function is used?", "Mid()", "Right()", "Len()", "Left()", "C"),
    ("A user-defined function in VBA is created using:", "Sub...End Sub", "Function...End Function", "Loop...End Loop", "Case...End Case", "B"),
    ("In VBA, which object represents a single cell or a group of cells in Excel?", "Workbook", "Worksheet", "Range", "Module", "C"),
    ("Which function returns the upper boundary index of an array in VBA?", "Len()", "UBound()", "Mid()", "Array()", "B")
]

# Insert into respective tables
cur.executemany("INSERT INTO battle_questions (question, option1, option2, option3, option4, correct_answer) VALUES (?, ?, ?, ?, ?, ?)", cloud_questions)
cur.executemany("INSERT INTO survival_questions (question, option1, option2, option3, option4, correct_answer) VALUES (?, ?, ?, ?, ?, ?)", vba_questions)

conn.commit()
conn.close()

print("Database successfully rebuilt with separate Battle and Survival tables!")
