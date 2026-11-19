import os

from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QMessageBox
from PyQt5.uic import loadUi


class ResultWindow(QDialog):
    def __init__(self, user, score, total_questions, subject_name="", parent=None):
        super().__init__(parent)

        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "CBTResultPage.ui")
        loadUi(ui_path, self)

        self.user = user
        self.score = int(score)
        self.total_questions = int(total_questions)
        self.subject_name = subject_name

        self.error_label = self.findChild(QLabel, "error_label")
        self.success_label = self.findChild(QLabel, "success_label")
        self.score_label = self.findChild(QLabel, "score_label")
        self.result_title = self.findChild(QLabel, "result_title")
        self.feedback_label = self.findChild(QLabel, "feedback_label")
        self.student_subject_label = self.findChild(QLabel, "student_subject_label")
        self.correct_label = self.findChild(QLabel, "correct_label")
        self.wrong_label = self.findChild(QLabel, "wrong_label")
        self.percent_label = self.findChild(QLabel, "percent_label")
        self.dashboard_btn = self.findChild(QPushButton, "dashboard_btn")

        if self.error_label is not None:
            self.error_label.hide()
        if self.success_label is not None:
            self.success_label.hide()

        self.render_result()

        if self.dashboard_btn is not None:
            self.dashboard_btn.clicked.connect(self.go_to_dashboard)

    def render_result(self):
        total = self.total_questions
        wrong = max(0, total - self.score)
        percent = int((self.score / total) * 100) if total > 0 else 0
        passed = percent >= 50
        student_name = str(self.user[1]) if self.user and len(self.user) > 1 else "Student"
        if self.student_subject_label is not None:
            if self.subject_name:
                self.student_subject_label.setText(f"{student_name} - {self.subject_name}")
            else:
                self.student_subject_label.setText(student_name)

        if self.score_label is not None:
            self.score_label.setText(f"{self.score}/{self.total_questions}")
        if self.correct_label is not None:
            self.correct_label.setText(f"Correct\n{self.score}")
        if self.wrong_label is not None:
            self.wrong_label.setText(f"Wrong\n{wrong}")
        if self.percent_label is not None:
            self.percent_label.setText(f"{percent}%")

        if self.result_title is not None:
            self.result_title.setText("Well Done!" if passed else "Keep Trying!")
        if self.feedback_label is not None:
            self.feedback_label.setText(
                "You passed the quiz!!!" if passed else "You did not pass this time."
            )
            self.feedback_label.setStyleSheet(
                "QLabel { color: #6FCF6F; font: 13px 'Segoe UI'; }"
                if passed
                else "QLabel { color: #CF6F6F; font: 13px 'Segoe UI'; }"
            )

        if self.score_label is not None:
            self.score_label.setStyleSheet(
                "QLabel { color: #6FCF6F; font: bold 28px 'Segoe UI'; border: 3px solid #6FCF6F; border-radius: 75px; }"
                if passed
                else "QLabel { color: #CF6F6F; font: bold 28px 'Segoe UI'; border: 3px solid #CF6F6F; border-radius: 75px; }"
            )

    def go_to_dashboard(self):
        try:
            from windows.student_dashboard import StudentDashboard

            self.dashboard = StudentDashboard(self.user)
            self.dashboard.show()
            self.close()
        except Exception as exc:
            QMessageBox.warning(self, "Navigation error", f"Could not open dashboard: {exc}")