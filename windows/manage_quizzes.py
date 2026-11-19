from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import os


class ManageQuizzes(QDialog):
    def __init__(self, user, subject_id, subject_name, parent=None):
        super(ManageQuizzes, self).__init__(parent)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "CBTManageQuizzes.ui")
        loadUi(ui_path, self)

        self.user = user
        self.subject_id = subject_id
        self.subject_name = subject_name

        self.subjectLabel = self.findChild(QLabel, "subjectLabel")
        self.quiz_input = self.findChild(QLineEdit, "quiz_input")
        self.add_quiz_btn = self.findChild(QPushButton, "add_quiz_btn")
        self.quizzes_table = self.findChild(QTableWidget, "quizzes_table")
        self.open_questions_btn = self.findChild(QPushButton, "open_questions_btn")
        self.delete_btn = self.findChild(QPushButton, "delete_btn")
        self.back_btn = self.findChild(QPushButton, "back_btn")
        self.error_label = self.findChild(QLabel, "error_label")
        self.success_label = self.findChild(QLabel, "success_label")

        if self.error_label is not None:
            self.error_label.hide()
        if self.success_label is not None:
            self.success_label.hide()

        if self.subjectLabel is not None:
            self.subjectLabel.setText(f"Subject: {self.subject_name}")

        if self.quizzes_table is not None:
            self.quizzes_table.setColumnCount(2)
            self.quizzes_table.setHorizontalHeaderLabels(["ID", "Quiz Title"])
            self.quizzes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.quizzes_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.quizzes_table.setSelectionBehavior(QTableWidget.SelectRows)

        self.load_quizzes()

        if self.add_quiz_btn is not None:
            self.add_quiz_btn.clicked.connect(self.add_quiz)
        if self.open_questions_btn is not None:
            self.open_questions_btn.clicked.connect(self.open_questions)
        if self.delete_btn is not None:
            self.delete_btn.clicked.connect(self.delete_quiz)
        if self.back_btn is not None:
            self.back_btn.clicked.connect(self.go_back)

    def show_error(self, message):
        if self.success_label is not None:
            self.success_label.hide()
        if self.error_label is not None:
            self.error_label.setText(message)
            self.error_label.show()

    def show_success(self, message):
        if self.error_label is not None:
            self.error_label.hide()
        if self.success_label is not None:
            self.success_label.setText(message)
            self.success_label.show()

    def load_quizzes(self):
        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT ID, Title FROM Quizzes WHERE SubjectID = ?",
            (self.subject_id,)
        )
        rows = cur.fetchall()
        conn.close()

        if self.quizzes_table is None:
            return

        self.quizzes_table.setRowCount(0)
        for row_data in rows:
            row = self.quizzes_table.rowCount()
            self.quizzes_table.insertRow(row)
            for col, val in enumerate(row_data):
                self.quizzes_table.setItem(row, col, QTableWidgetItem(str(val)))

    def add_quiz(self):
        if self.quiz_input is None:
            self.show_error("Quiz input is missing from this UI.")
            return

        title = self.quiz_input.text().strip()
        if not title:
            self.show_error("Please enter a quiz title.")
            return

        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Quizzes (Title, SubjectID, CreatedBy) VALUES (?, ?, ?)",
            (title, self.subject_id, self.user[0])
        )
        conn.commit()
        conn.close()

        self.show_success(f"Quiz '{title}' created.")
        self.quiz_input.clear()
        self.load_quizzes()

    def open_questions(self):
        if self.quizzes_table is None:
            self.show_error("Quizzes table is missing from this UI.")
            return
        selected = self.quizzes_table.currentRow()
        if selected < 0:
            self.show_error("Please select a quiz first.")
            return

        quiz_id = self.quizzes_table.item(selected, 0).text()
        quiz_title = self.quizzes_table.item(selected, 1).text()

        from windows.manage_questions import ManageQuestions
        self.window = ManageQuestions(self.user, int(quiz_id), quiz_title,
                                      self.subject_id, self.subject_name)
        self.window.show()
        self.close()

    def delete_quiz(self):
        if self.quizzes_table is None:
            self.show_error("Quizzes table is missing from this UI.")
            return
        selected = self.quizzes_table.currentRow()
        if selected < 0:
            self.show_error("Please select a quiz to delete.")
            return

        quiz_id = self.quizzes_table.item(selected, 0).text()
        quiz_title = self.quizzes_table.item(selected, 1).text()

        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM Questions WHERE QuizID = ?", (quiz_id,))
        cur.execute("DELETE FROM Quizzes WHERE ID = ?", (quiz_id,))
        conn.commit()
        conn.close()

        self.show_success(f"Quiz '{quiz_title}' deleted.")
        self.load_quizzes()

    def go_back(self):
        from windows.manage_subjects import ManageSubjects
        self.window = ManageSubjects(self.user)
        self.window.show()
        self.close()