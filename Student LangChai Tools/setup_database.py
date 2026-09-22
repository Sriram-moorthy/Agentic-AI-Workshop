import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("students.db")

STUDENTS = [
    ("22CS045", "Dhanushya", "Computer Science", 85, 72, 90, 78),
    ("22CS046", "Rahul", "Computer Science", 65, 70, 68, 72),
    ("22CS047", "Priya", "Information Technology", 92, 88, 95, 90),
    ("22CS048", "Arun", "Information Technology", 55, 60, 58, 62),
    ("22CS049", "Meena", "Computer Science", 78, 85, 80, 88),
]


def initialize_database() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                python INTEGER NOT NULL CHECK (python BETWEEN 0 AND 100),
                database_mark INTEGER NOT NULL CHECK (database_mark BETWEEN 0 AND 100),
                ai INTEGER NOT NULL CHECK (ai BETWEEN 0 AND 100),
                web INTEGER NOT NULL CHECK (web BETWEEN 0 AND 100)
            )
            """
        )

        conn.executemany(
            """
            INSERT OR REPLACE INTO students
            (student_id, name, department, python, database_mark, ai, web)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            STUDENTS,
        )

    print(f"Database initialized: {DB_PATH}")


if __name__ == "__main__":
    initialize_database()
