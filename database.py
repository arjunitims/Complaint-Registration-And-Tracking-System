import sqlite3
from datetime import datetime

DB_NAME = "complaints.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        category TEXT NOT NULL,
        complaint_text TEXT NOT NULL,
        priority TEXT,
        estimated_resolution_hours REAL,
        status TEXT,
        submitted_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def insert_complaint(
    name,
    email,
    phone,
    category,
    complaint_text,
    priority,
    estimated_hours,
    status
):
    conn = get_connection()
    c = conn.cursor()

    submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("""
    INSERT INTO complaints
    (name, email, phone, category,
     complaint_text, priority,
     estimated_resolution_hours, status, submitted_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        email,
        phone,
        category,
        complaint_text,
        priority,
        estimated_hours,
        status,
        submitted_at
    ))

    conn.commit()
    complaint_id = c.lastrowid
    conn.close()

    return complaint_id

def get_all_complaints():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM complaints ORDER BY id DESC")
    rows = c.fetchall()

    conn.close()
    return rows
def update_complaint_status(complaint_id, new_status):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "UPDATE complaints SET status = ? WHERE id = ?",
        (new_status, complaint_id)
    )

    conn.commit()
    conn.close()