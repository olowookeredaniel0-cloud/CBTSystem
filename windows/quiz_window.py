from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer, Qt
import random
import os


class QuizWindow(QDialog):
    def __init__(self, user, quiz_id, quiz_title, subject_name="", parent=None):
        super(QuizWindow, self).__init__(parent)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "CBTQuizPage.ui")
        loadUi(ui_path, self)

        self.user = user
        self.quiz_id = quiz_id
        self.quiz_title = quiz_title
        self.subject_name = subject_name
        self.timer_label = self.findChild(QLabel, "timer_label")
        self.progress_label = self.findChild(QLabel, "progress_label")
        self.quiz_progressbar = self.findChild(QProgressBar, "quiz_progressbar")
        self.question_label = self.findChild(QLabel, "question_label")
        self.option_a_btn = self.findChild(QPushButton, "option_a_btn")
        self.option_b_btn = self.findChild(QPushButton, "option_b_btn")
        self.option_c_btn = self.findChild(QPushButton, "option_c_btn")
        self.option_d_btn = self.findChild(QPushButton, "option_d_btn")
        self.next_btn = self.findChild(QPushButton, "next_btn")
        self.submit_btn = self.findChild(QPushButton, "submit_btn")
        self.error_label = self.findChild(QLabel, "error_label")

        if self.error_label is None:
            self.error_label.hide()
        if self.submit_btn is not None:
            self.submit_btn.hide()

        self.questions = self.load_questions()
        self.current_index = 0
        self.selected_answer = None
        self.score = 0

        self.time_left = 1200
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        self.load_question()

        if self.option_a_btn is not None:
            self.option_a_btn.clicked.connect(lambda: self.select_option("A"))
        if self.option_b_btn is not None:
            self.option_b_btn.clicked.connect(lambda: self.select_option("B"))
        if self.option_c_btn is not None:
            self.option_c_btn.clicked.connect(lambda: self.select_option("C"))
        if self.option_d_btn is not None:
            self.option_d_btn.clicked.connect(lambda: self.select_option("D"))
        if self.next_btn is not None:
            self.next_btn.clicked.connect(self.next_question)
        if self.submit_btn is not None:
            self.submit_btn.clicked.connect(self.submit_quiz)

    def load_questions(self):
        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        # Fetch questions for this specific quiz
        cur.execute("SELECT * FROM Questions WHERE QuizID = ?", (self.quiz_id,))
        questions = cur.fetchall()
        conn.close()
        random.shuffle(questions)
        return questions

    def load_question(self):
        self.selected_answer = None
        self.error_label.hide()

        # q[0]=ID, q[1]=QuizID, q[2]=QuestionText,
        # q[3]=OptionA, q[4]=OptionB, q[5]=OptionC, q[6]=OptionD, q[7]=CorrectAnswer
        q = self.questions[self.current_index]

        self.question_label.setText(q[2])
        self.option_a_btn.setText(f"  A.   {q[3]}")
        self.option_b_btn.setText(f"  B.   {q[4]}")
        self.option_c_btn.setText(f"  C.   {q[5]}")
        self.option_d_btn.setText(f"  D.   {q[6]}")

        total = len(self.questions)
        current = self.current_index + 1
        self.progress_label.setText(f"Question {current} of {total}")
        self.quiz_progressbar.setValue(int((current / total) * 100))

        if self.current_index == total - 1:
            self.next_btn.hide()
            self.submit_btn.show()
        else:
            self.next_btn.show()
            self.submit_btn.hide()

    def select_option(self, letter):
        self.selected_answer = letter
        self.error_label.hide()

    def next_question(self):
        if self.selected_answer is None:
            self.error_label.setText("Please select an answer before proceeding.")
            self.error_label.show()
            return

        # q[7] is CorrectAnswer
        if self.selected_answer == self.questions[self.current_index][7]:
            self.score += 1

        self.current_index += 1
        self.load_question()

    def submit_quiz(self):
        if self.selected_answer is None:
            self.error_label.setText("Please select an answer before submitting.")
            self.error_label.show()
            return

        if self.selected_answer == self.questions[self.current_index][7]:
            self.score += 1

        self.timer.stop()
        self.save_result()
        self.open_result()

    def update_timer(self):
        self.time_left -= 1
        mins = self.time_left // 60
        secs = self.time_left % 60
        self.timer_label.setText(f"{mins:02d}:{secs:02d}")

        if self.time_left <= 0:
            self.timer.stop()
            self.save_result()
            self.open_result()

    def save_result(self):
        from database import create_connection
        from datetime import datetime
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Results (StudentID, QuizID, Score, TotalQuestions, Date) VALUES (?, ?, ?, ?, ?)",
            (self.user[0], self.quiz_id, self.score,
             len(self.questions), datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        conn.commit()
        conn.close()

    def open_result(self):
        from windows.result_window import ResultWindow
        self.result = ResultWindow(
            self.user,
            self.score,
            len(self.questions),
            self.subject_name
        )
        self.result.show()
        self.close()