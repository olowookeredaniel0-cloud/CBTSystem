from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import os


class StudentDashboard(QDialog):
    def __init__(self, user, parent=None):
        super(StudentDashboard, self).__init__(parent)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "CBTStudentDashboard.ui")
        loadUi(ui_path, self)

        self.user = user

        self.welcome_label = self.findChild(QLabel, "welcome_label")
        self.subject_combo_box = self.findChild(QComboBox, "subject_combo_box")
        self.quiz_list = self.findChild(QListWidget, "quiz_list")
        self.start_quiz_btn = self.findChild(QPushButton, "start_quiz_btn")
        self.logout_btn = self.findChild(QPushButton, "logout_btn")
        self.error_label = self.findChild(QLabel, "error_label")
        self.role_label = self.findChild(QLabel, "role_label")

        if self.error_label is not None:
            self.error_label.hide()

        if self.welcome_label is not None:
            self.welcome_label.setText(f"Welcome, {self.user[1]}")
        if self.role_label is not None:
            self.role_label.setText(str(self.user[3]))

        # Load subjects into dropdown
        self.load_subjects()

        # When subject changes, load its quizzes
        if self.subject_combo_box is not None:
            self.subject_combo_box.currentIndexChanged.connect(self.load_quizzes)

        if self.start_quiz_btn is not None:
            self.start_quiz_btn.clicked.connect(self.start_quiz)
        if self.logout_btn is not None:
            self.logout_btn.clicked.connect(self.logout)

    def show_error(self, message):
        if self.error_label is not None:
            self.error_label.setText(message)
            self.error_label.show()

    def load_subjects(self):
        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT ID, Name FROM Subjects")
        self.subjects = cur.fetchall()
        conn.close()

        if self.subject_combo_box is None:
            return

        self.subject_combo_box.clear()
        if not self.subjects:
            self.subject_combo_box.addItem("No subjects available")
            return

        for s in self.subjects:
            self.subject_combo_box.addItem(s[1], s[0])  # display name, store ID

        # Load quizzes for first subject
        self.load_quizzes()

    def load_quizzes(self, *_):
        if self.quiz_list is None or self.subject_combo_box is None:
            return

        self.quiz_list.clear()
        if self.error_label is not None:
            self.error_label.hide()

        if not self.subjects:
            return

        # Get selected subject ID from combo box data
        subject_id = self.subject_combo_box.currentData()
        if subject_id is None:
            return

        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT ID, Title FROM Quizzes WHERE SubjectID = ?", (subject_id,))
        self.quizzes = cur.fetchall()
        conn.close()

        if not self.quizzes:
            self.quiz_list.addItem("No quizzes available for this subject")
            return

        for q in self.quizzes:
            item = QListWidgetItem(q[1])
            item.setData(32, q[0])  # store quiz ID in item data
            self.quiz_list.addItem(item)

    def start_quiz(self):
        try:
            selected = self.quiz_list.currentItem()
            if selected is None:
                self.show_error("Please select a quiz to start.")
                return

            quiz_id = selected.data(32)
            quiz_title = selected.text()
            subject_name = self.subject_combo_box.currentText() if self.subject_combo_box is not None else ""

            if quiz_title == "No quizzes available for this subject":
                self.show_error("No quiz to start.")
                return

            # Check questions exist for this quiz
            from database import create_connection
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM Questions WHERE QuizID = ?", (quiz_id,))
            count = cur.fetchone()[0]
            conn.close()

            if count == 0:
                self.show_error("This quiz has no questions yet.")
                return

            from windows.quiz_window import QuizWindow
            self.quiz = QuizWindow(self.user, quiz_id, quiz_title, subject_name=subject_name)
            self.quiz.show()
            self.close()
        except Exception as e:
            self.show_error(f"Could not start quiz: {e}")

    def logout(self):
        from windows.login_window import LoginWindow
        self.window = LoginWindow()
        self.window.show()
        self.close()