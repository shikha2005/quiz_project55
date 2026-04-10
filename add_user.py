import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

cur.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")

conn.commit()
conn.close()

print("Admin Added!")