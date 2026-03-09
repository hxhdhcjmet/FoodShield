import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "foodshield.db"
SCHEMA_PATH = BASE_DIR / "project" / "database" / "schema.sql"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def query_all(sql, params=()):
    conn = get_db_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def query_one(sql, params=()):
    conn = get_db_connection()
    row = conn.execute(sql, params).fetchone()
    conn.close()
    return row


def execute(sql, params=()):
    conn = get_db_connection()
    cursor = conn.execute(sql, params)
    conn.commit()
    lastrowid = cursor.lastrowid
    conn.close()
    return lastrowid