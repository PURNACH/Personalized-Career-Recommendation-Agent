
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "career_agent.db"


def connect():
    return sqlite3.connect(DB_PATH)


def initialize_db():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                education TEXT,
                experience REAL,
                skills TEXT,
                interests TEXT,
                goal TEXT,
                created_at TEXT
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                career TEXT NOT NULL,
                score REAL NOT NULL,
                FOREIGN KEY(profile_id) REFERENCES profiles(id)
            )
        """)


def save_profile(name, education, experience, skills, interests, goal):
    with connect() as db:
        cursor = db.execute("""
            INSERT INTO profiles
            (name, education, experience, skills, interests, goal, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name, education, experience, skills, interests, goal,
            datetime.now().isoformat(timespec="seconds"),
        ))

        return cursor.lastrowid


def save_recommendations(profile_id, results):
    with connect() as db:
        db.executemany("""
            INSERT INTO recommendations
            (profile_id, career, score)
            VALUES (?, ?, ?)
        """, [
            (profile_id, result["role"], result["score"])
            for result in results
        ])


def get_profiles():
    with connect() as db:
        return db.execute("""
            SELECT id, name, education, experience,
                   skills, interests, goal, created_at
            FROM profiles
            ORDER BY id DESC
        """).fetchall()


def get_profile_count():
    with connect() as db:
        return db.execute(
            "SELECT COUNT(*) FROM profiles"
        ).fetchone()[0]
