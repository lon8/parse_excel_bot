import sqlite3

DATABASE = 'websites.db'

def create_table():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS websites
                 (title TEXT, url TEXT, xpath TEXT)''')
    conn.commit()
    conn.close()

def save_to_db(data):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    for index, row in data.iterrows():
        c.execute("INSERT INTO websites (title, url, xpath) VALUES (?, ?, ?)",
                  (row['title'], row['url'], row['xpath']))
    conn.commit()
    conn.close()
