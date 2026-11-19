from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import os


class ManageSubjects(QDialog):
    def __init__(self, user, parent=None):
        super(ManageSubjects, self).__init__(parent)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "CBTManageSubjects.ui")
        loadUi(ui_path, self)

        self.user = user

        self.subject_input = self.findChild(QLineEdit, "subject_input")
        self.add_subject_btn = self.findChild(QPushButton, "add_subject_btn")
        self.subjects_table = self.findChild(QTableWidget, "subjects_table")
        self.open_quizzes_btn = self.findChild(QPushButton, "open_quizzes_btn") or self.findChild(QPushButton, "pushButton")
        self.delete_btn = self.findChild(QPushButton, "delete_btn")
        self.back_btn = self.findChild(QPushButton, "back_btn")
        self.error_label = self.findChild(QLabel, "error_label")
        self.success_label = self.findChild(QLabel, "success_label")

        if self.error_label is not None:
            self.error_label.hide()
        if self.success_label is not None:
            self.success_label.hide()

        if self.subjects_table is not None:
            self.subjects_table.setColumnCount(2)
            self.subjects_table.setHorizontalHeaderLabels(["ID", "Subject Name"])
            self.subjects_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.subjects_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.subjects_table.setSelectionBehavior(QTableWidget.SelectRows)

        self.load_subjects()

        if self.add_subject_btn is not None:
            self.add_subject_btn.clicked.connect(self.add_subject)
        if self.open_quizzes_btn is not None:
            self.open_quizzes_btn.clicked.connect(self.open_quizzes)
        if self.delete_btn is not None:
            self.delete_btn.clicked.connect(self.delete_subject)
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

    def load_subjects(self):
        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        # Admin only sees their own subjects
        cur.execute(
            "SELECT ID, Name FROM Subjects WHERE CreatedBy = ?",
            (self.user[0],)
        )
        rows = cur.fetchall()
        conn.close()

        if self.subjects_table is None:
            return
        self.subjects_table.setRowCount(0)
        for row_data in rows:
            row = self.subjects_table.rowCount()
            self.subjects_table.insertRow(row)
            for col, val in enumerate(row_data):
                self.subjects_table.setItem(row, col, QTableWidgetItem(str(val)))

    def add_subject(self):
        if self.subject_input is None:
            self.show_error("Subject form is missing input field.")
            return
        name = self.subject_input.text().strip()
        if not name:
            self.show_error("Please enter a subject name.")
            return

        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Subjects (Name, CreatedBy) VALUES (?, ?)",
            (name, self.user[0])
        )
        conn.commit()
        conn.close()

        self.show_success(f"Subject '{name}' created.")
        self.subject_input.clear()
        self.load_subjects()

    def open_quizzes(self):
        if self.subjects_table is None:
            self.show_error("Subjects table is missing from this UI.")
            return
        selected = self.subjects_table.currentRow()
        if selected < 0:
            self.show_error("Please select a subject first.")
            return

        subject_id = self.subjects_table.item(selected, 0).text()
        subject_name = self.subjects_table.item(selected, 1).text()

        from windows.manage_quizzes import ManageQuizzes
        self.window = ManageQuizzes(self.user, int(subject_id), subject_name)
        self.window.show()
        self.close()

    def delete_subject(self):
        if self.subjects_table is None:
            self.show_error("Subjects table is missing from this UI.")
            return
        selected = self.subjects_table.currentRow()
        if selected < 0:
            self.show_error("Please select a subject to delete.")
            return

        subject_id = self.subjects_table.item(selected, 0).text()
        subject_name = self.subjects_table.item(selected, 1).text()

        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        # Delete subject — quizzes and questions under it are also deleted
        cur.execute("DELETE FROM Questions WHERE QuizID IN (SELECT ID FROM Quizzes WHERE SubjectID = ?)", (subject_id,))
        cur.execute("DELETE FROM Quizzes WHERE SubjectID = ?", (subject_id,))
        cur.execute("DELETE FROM Subjects WHERE ID = ?", (subject_id,))
        conn.commit()
        conn.close()

        self.show_success(f"Subject '{subject_name}' and all its quizzes deleted.")
        self.load_subjects()

    def go_back(self):
        from windows.admin_dashboard import AdminDashboard
        self.window = AdminDashboard(self.user)
        self.window.show()
        self.close()