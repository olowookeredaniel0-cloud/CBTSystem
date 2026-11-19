from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import os


class ManageQuestions(QDialog):
    def __init__(self, user, quiz_id, quiz_title, subject_id, subject_name, parent=None):
        super(ManageQuestions, self).__init__(parent)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "CBTManageQuestions.ui")
        loadUi(ui_path, self)

        self.user = user
        self.quiz_id = quiz_id
        self.quiz_title = quiz_title
        self.subject_id = subject_id
        self.subject_name = subject_name

        self.quizLabel = self.findChild(QLabel, "quizLabel")
        self.question_input = self.findChild(QLineEdit, "question_input")
        self.option_a_input = self.findChild(QLineEdit, "option_a_input")
        self.option_b_input = self.findChild(QLineEdit, "option_b_input")
        self.option_c_input = self.findChild(QLineEdit, "option_c_input")
        self.option_d_input = self.findChild(QLineEdit, "option_d_input")
        self.correct_answer_box = self.findChild(QComboBox, "correct_ans_box")
        self.add_question_btn = self.findChild(QPushButton, "add_question_btn")
        self.questions_table = self.findChild(QTableWidget, "questions_table")
        self.delete_btn = self.findChild(QPushButton, "delete_btn")
        self.back_btn = self.findChild(QPushButton, "back_btn")
        self.error_label = self.findChild(QLabel, "error_label")
        self.success_label = self.findChild(QLabel, "success_label")

        if self.error_label is not None:
            self.error_label.hide()
        if self.success_label is not None:
            self.success_label.hide()

        if self.quizLabel is not None:
            self.quizLabel.setText(f"Quiz: {self.quiz_title}")

        if self.correct_answer_box is not None:
            self.correct_answer_box.addItems(["A", "B", "C", "D"])

        if self.questions_table is not None:
            self.questions_table.setColumnCount(3)
            self.questions_table.setHorizontalHeaderLabels(["ID", "Question", "Answer"])
            self.questions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.questions_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.questions_table.setSelectionBehavior(QTableWidget.SelectRows)

        self.load_questions()

        if self.add_question_btn is not None:
            self.add_question_btn.clicked.connect(self.add_question)
        if self.delete_btn is not None:
            self.delete_btn.clicked.connect(self.delete_question)
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

    def load_questions(self):
        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT ID, QuestionText, CorrectAnswer FROM Questions WHERE QuizID = ?",
            (self.quiz_id,)
        )
        rows = cur.fetchall()
        conn.close()

        if self.questions_table is None:
            return

        self.questions_table.setRowCount(0)
        for row_data in rows:
            row = self.questions_table.rowCount()
            self.questions_table.insertRow(row)
            for col, val in enumerate(row_data):
                self.questions_table.setItem(row, col, QTableWidgetItem(str(val)))

    def add_question(self):
        if (
            self.question_input is None
            or self.option_a_input is None
            or self.option_b_input is None
            or self.option_c_input is None
            or self.option_d_input is None
            or self.correct_answer_box is None
        ):
            self.show_error("Question form is missing fields in this UI.")
            return

        question = self.question_input.text().strip()
        opt_a = self.option_a_input.text().strip()
        opt_b = self.option_b_input.text().strip()
        opt_c = self.option_c_input.text().strip()
        opt_d = self.option_d_input.text().strip()
        correct = self.correct_answer_box.currentText()

        if not question or not opt_a or not opt_b or not opt_c or not opt_d:
            self.show_error("Please fill in all fields.")
            return

        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Questions (QuizID, QuestionText, OptionA, OptionB, OptionC, OptionD, CorrectAnswer) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (self.quiz_id, question, opt_a, opt_b, opt_c, opt_d, correct)
        )
        conn.commit()
        conn.close()

        self.show_success("Question added successfully.")
        self.question_input.clear()
        self.option_a_input.clear()
        self.option_b_input.clear()
        self.option_c_input.clear()
        self.option_d_input.clear()
        self.correct_answer_box.setCurrentIndex(0)
        self.load_questions()

    def delete_question(self):
        if self.questions_table is None:
            self.show_error("Questions table is missing from this UI.")
            return
        selected = self.questions_table.currentRow()
        if selected < 0:
            self.show_error("Please select a question to delete.")
            return

        question_id = self.questions_table.item(selected, 0).text()

        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM Questions WHERE ID = ?", (question_id,))
        conn.commit()
        conn.close()

        self.show_success("Question deleted.")
        self.load_questions()

    def go_back(self):
        from windows.manage_quizzes import ManageQuizzes
        self.window = ManageQuizzes(self.user, self.subject_id, self.subject_name)
        self.window.show()
        self.close()