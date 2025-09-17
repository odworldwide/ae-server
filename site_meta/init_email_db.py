import sqlite3

def init_db():
	conn = None
	try:
		conn = sqlite3.connect('../mail.db')
		c=conn.cursor()
		c.execute('''DROP TABLE IF EXISTS mail''')
		c.execute('''CREATE TABLE IF NOT EXISTS mail
			(id INTEGER PRIMARY KEY, 'timestamp' DATETIME DEFAULT CURRENT_TIMESTAMP, email TEXT)''')
		print(sqlite3.version)
	except sqlite3.Error as e:
		print(e)
	finally:
		if conn:
			conn.close()


if __name__ == "__main__":
	init_db()