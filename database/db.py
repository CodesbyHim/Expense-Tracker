import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "spendly.db")


def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Creates all tables using CREATE TABLE IF NOT EXISTS."""
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()
    finally:
        conn.close()


def create_user(name, email, password):
    """Creates a user and returns the new user ID."""
    conn = get_db()
    try:
        password_hash = generate_password_hash(password)
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def seed_db():
    """Inserts sample data for development if not already present."""
    conn = get_db()
    try:
        existing = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()
        if existing["count"] > 0:
            return

        password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash)
        )
        user_id = cursor.lastrowid

        expenses = [
            (user_id, 15.50, "Food", "2026-05-02", "Lunch at cafe"),
            (user_id, 45.00, "Transport", "2026-05-03", "Taxi to airport"),
            (user_id, 120.00, "Bills", "2026-05-05", "Electricity bill"),
            (user_id, 30.00, "Health", "2026-05-06", "Pharmacy"),
            (user_id, 25.00, "Entertainment", "2026-05-08", "Movie tickets"),
            (user_id, 85.00, "Shopping", "2026-05-10", "New shoes"),
            (user_id, 12.00, "Other", "2026-05-11", "Miscellaneous"),
            (user_id, 55.00, "Food", "2026-05-12", "Grocery shopping"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()
    finally:
        conn.close()