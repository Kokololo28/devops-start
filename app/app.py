import os
import time
import psycopg2
from flask import Flask

app = Flask(__name__)

def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "localhost"),
                database=os.environ.get("DB_NAME", "postgres"),
                user=os.environ.get("DB_USER", "postgres"),
                password=os.environ.get("DB_PASS", "postgres")
            )
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            print(f"Database not ready, waiting 1 second... ({retries} retries left)")
            time.sleep(1)
    raise Exception("Could not connect to database after multiple retries.")

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS hits (count INTEGER);')
    cur.execute('SELECT * FROM hits;')
    if cur.fetchone() is None:
        cur.execute('INSERT INTO hits (count) VALUES (0);')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def hello():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE hits SET count = count + 1 RETURNING count;')
    count = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return f'<h1>Hello DevOps!</h1><p>This page has been visited {count} times.</p>'

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)