import sqlite3

DATABASE = "foodshield.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    with open("project/database/schema.sql", "r") as f:
        conn.executescript(f.read())

    conn.commit()
    conn.close()