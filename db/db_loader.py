import psycopg2

DB_URL = "dbname=ivf user=postgres password=pass host=localhost"

def load_all_clinics():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT * FROM clinics;")
    cols = [desc[0] for desc in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return rows
