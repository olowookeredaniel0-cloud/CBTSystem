import random
import string
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import os

PASSWORD_LENGTH = 8

class ManageStudents(QDialog):
    def __init__(self, user, parent=None):
        super(ManageStudents, self).__init__(parent)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_candidates = [
            os.path.join(base_dir, "ui", "CBTManageStudents.ui"),
            os.path.join(base_dir, "ui", "ManageStudents.ui"),
            os.path.join(base_dir, "ui", "CBTManageAdmins.ui"),
        ]
        ui_path = next((path for path in ui_candidates if os.path.exists(path)), None)
        if ui_path is None:
            raise FileNotFoundError("No compatible manage-students UI file found in ui folder.")
        loadUi(ui_path, self)
        self.user = user
        self.username_input = self.findChild(QLineEdit, "username_input")
        self.gen_pwd_label = self.findChild(QLabel, "gen_pwd_label") 
        self.add_student_btn = self.findChild(QPushButton, "add_student_btn")
        self.students_table = (
            self.findChild(QTableWidget, "students_table")
            or self.findChild(QTableWidget, "student_table")
            or self.findChild(QTableWidget, "admins_table")
        )
        self.delete_btn = self.findChild(QPushButton, "delete_btn")
        self.back_btn = self.findChild(QPushButton, "back_btn") or self.findChild(QPushButton, "pushButton")
        self.error_label = self.findChild(QLabel, "error_label")
        self.success_label = self.findChild(QLabel, "success_label")

        if self.error_label is not None:
            self.error_label.hide()
        if self.success_label is not None:
            self.success_label.hide()

        # Set up table
        if self.students_table is not None:
            self.students_table.setColumnCount(3)
            self.students_table.setHorizontalHeaderLabels(["ID", "Username", "Role"])
            self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.students_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.students_table.setSelectionBehavior(QTableWidget.SelectRows)

        # Show an initial generated password
        if self.gen_pwd_label is not None:
            self.gen_pwd_label.setText(f"Generated password: {self.generate_password()}")

        self.load_students()

        if self.add_student_btn is not None:
            self.add_student_btn.clicked.connect(self.add_student)
        if self.delete_btn is not None:
            self.delete_btn.clicked.connect(self.delete_student)
        if self.back_btn is not None:
            self.back_btn.clicked.connect(self.go_back)

    def generate_password(self):
        # Auto-generates a random 8-character password
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=8))

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

    def load_students(self):
        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT ID, Username, Role FROM Users WHERE LOWER(REPLACE(Role, ' ', '')) = 'student'")
        rows = cur.fetchall()
        conn.close()

        if self.students_table is None:
            return
        self.students_table.setRowCount(0)
        for row_data in rows:
            row = self.students_table.rowCount()
            self.students_table.insertRow(row)
            for col, val in enumerate(row_data):
                self.students_table.setItem(row, col, QTableWidgetItem(str(val)))

    def add_student(self):
        if self.username_input is None:
            self.show_error("Student form is missing username field.")
            return
        username = self.username_input.text().strip()

        if not username:
            self.show_error("Please enter a username.")
            return

        # Auto-generate password
        password = self.generate_password()

        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()

        cur.execute("SELECT ID FROM Users WHERE Username = ?", (username,))
        if cur.fetchone():
            self.show_error("Username already exists.")
            conn.close()
            return

        cur.execute(
            "INSERT INTO Users (Username, Password, Role, CreatedBy) VALUES (?, ?, 'Student', ?)",
            (username, password, self.user[0])
        )
        conn.commit()
        conn.close()

        # Show generated credentials clearly
        if self.gen_pwd_label is not None:
            self.gen_pwd_label.setText(f"Generated password: {password}")
        self.show_success(f"Student '{username}' created! Password: {password}")
        self.username_input.clear()
        self.load_students()

    def delete_student(self):
        if self.students_table is None:
            self.show_error("Students table is missing from this UI.")
            return
        selected = self.students_table.currentRow()
        if selected < 0:
            self.show_error("Please select a student to delete.")
            return

        student_id = self.students_table.item(selected, 0).text()
        student_name = self.students_table.item(selected, 1).text()

        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM Users WHERE ID = ?", (student_id,))
        conn.commit()
        conn.close()

        self.show_success(f"Student '{student_name}' deleted.")
        self.load_students()

    def go_back(self):
        from windows.super_admin import SuperAdminDashboard
        self.window = SuperAdminDashboard(self.user)
        self.window.show()
        self.close()