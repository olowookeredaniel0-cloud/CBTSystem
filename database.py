import sqlite3
import os

# This builds the path relative to THIS file's location
# no matter where the project folder is
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "CBT.db")


def create_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL,
            Role TEXT NOT NULL CHECK(Role IN ('Super Admin', 'Admin', 'Student')),
            CreatedBy INTEGER,
            FOREIGN KEY (CreatedBy) REFERENCES Users(ID)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Subjects (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            CreatedBy INTEGER NOT NULL,
            FOREIGN KEY (CreatedBy) REFERENCES Users(ID)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Quizzes (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT NOT NULL,
            SubjectID INTEGER NOT NULL,
            CreatedBy INTEGER NOT NULL,
            FOREIGN KEY (SubjectID) REFERENCES Subjects(ID),
            FOREIGN KEY (CreatedBy) REFERENCES Users(ID)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Questions (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            QuizID INTEGER NOT NULL,
            QuestionText TEXT NOT NULL,
            OptionA TEXT NOT NULL,
            OptionB TEXT NOT NULL,
            OptionC TEXT NOT NULL,
            OptionD TEXT NOT NULL,
            CorrectAnswer TEXT NOT NULL,
            FOREIGN KEY (QuizID) REFERENCES Quizzes(ID)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Results (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentID INTEGER NOT NULL,
            QuizID INTEGER NOT NULL,
            Score INTEGER NOT NULL,
            TotalQuestions INTEGER NOT NULL,
            Date TEXT NOT NULL,
            FOREIGN KEY (StudentID) REFERENCES Users(ID),
            FOREIGN KEY (QuizID) REFERENCES Quizzes(ID)
        )
    """)

    # Create default superadmin on first run
    cur.execute("SELECT COUNT(*) FROM Users WHERE Role = 'Super Admin'")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO Users (Username, Password, Role) VALUES (?, ?, ?)",
            ("Superadmin", "Admin@123", "Super Admin")
        )
        print("Default superadmin created — Username: Superadmin | Password: Admin@123")

    conn.commit()
    conn.close()
    print("Database ready at:", DB_PATH)


if __name__ == "__main__":
    create_tables()