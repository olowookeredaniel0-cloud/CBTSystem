from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import os

VALID_ANSWERS = ["A", "B", "C", "D"]

# Creating the class AddQuestion
class AddQuestion(QDialog):
    def __init__(self, user, parent=None):
        super(AddQuestion, self).__init__(parent)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "CBTAddQuestion.ui")
        loadUi(ui_path, self)
        self.user = user
        self.question_input = self.findChild(QLineEdit, "question_input")
        self.option_a_input = self.findChild(QLineEdit, "option_a_input")
        self.option_b_input = self.findChild(QLineEdit, "option_b_input")
        self.option_c_input = self.findChild(QLineEdit, "option_c_input")
        self.option_d_input = self.findChild(QLineEdit, "option_d_input")
        self.correct_answer_box = self.findChild(QComboBox, "correct_answer_box") or self.findChild(QComboBox, "comboBox")
        self.save_btn = self.findChild(QPushButton, "save_btn")
        self.back_btn = self.findChild(QPushButton, "back_btn")
        self.error_label = self.findChild(QLabel, "error_label")
        self.success_label = self.findChild(QLabel, "success_label")

        # Hiding the message labels
        if self.error_label is not None:
            self.error_label.hide()
        if self.success_label is not None:
            self.success_label.hide()

        # Populate correct answer dropdown
        if self.correct_answer_box is not None:
            self.correct_answer_box.clear()
            self.correct_answer_box.addItems(["A", "B", "C", "D"])
            self.correct_answer_box.setEditable(False)

        # Connecting the buttons
        if self.save_btn is not None:
            self.save_btn.clicked.connect(self.save_question)
        if self.back_btn is not None:
            self.back_btn.clicked.connect(self.go_back)

    def show_error(self):
        if self.success_label is not None:
            self.success_label.hide()
        if self.error_label is not None:
            self.error_label.setText("Question form is not fully loaded.")
            self.error_label.show()

    def show_success(self):
        if self.error_label is not None:
            self.error_label.hide()
        if self.success_label is not None:
            self.success_label.setText("Question saved successfully!")
            self.success_label.show()

    def save_question(self):
        if None in (self.question_input, self.option_a_input, self.option_b_input, self.option_c_input, self.option_d_input, self.correct_answer_box):
            self.show_error("Question form is not fully loaded.")
            return

        question = self.question_input.text().strip()
        option_a = self.option_a_input.text().strip()
        option_b = self.option_b_input.text().strip()
        option_c = self.option_c_input.text().strip()
        option_d = self.option_d_input.text().strip()
        correct = self.correct_answer_box.currentText()

        # Check no field is empty
        if not question or not option_a or not option_b or not option_c or not option_d:
            self.show_error("Please fill in all fields.")
            return

        # Save to database
        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Questions (Question, `Option A`, `Option B`, `Option C`, `Option D`, `Correct Answer`) VALUES (?, ?, ?, ?, ?, ?)",
            (question, option_a, option_b, option_c, option_d, correct)
        )
        conn.commit()
        conn.close()

        # Show success and clear all fields
        self.show_success("Question saved successfully!")
        self.question_input.clear()
        self.option_a_input.clear()
        self.option_b_input.clear()
        self.option_c_input.clear()
        self.option_d_input.clear()
        self.correct_answer_box.setCurrentIndex(0)

    def go_back(self):
        from windows.admin_dashboard import AdminDashboard
        self.admin = AdminDashboard(self.user)
        self.admin.show()
        self.close()