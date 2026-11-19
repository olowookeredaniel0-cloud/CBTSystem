from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import os

# Creating the class
class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "CBTLoginPage.ui")
        loadUi(ui_path, self)
        self.username_input = self.findChild(QLineEdit, "username_input")
        self.pwd_input = self.findChild(QLineEdit, "pwd_input")
        self.login_btn = self.findChild(QPushButton, "login_btn")
        self.toggle_pwd_btn = self.findChild(QPushButton, "toggle_pwd_btn")
        self.error_label = self.findChild(QLabel, "error_label")
        self.selected_role = ""

        # Hiding the error label
        if self.error_label is not None:
            self.error_label.hide()

        # Hide Password
        if self.pwd_input is not None:
            self.pwd_input.setEchoMode(QLineEdit.Password)
        self.password_visible = False

        # Connecting the buttons
        if self.login_btn is not None:
            self.login_btn.clicked.connect(self.handle_login)
        if self.toggle_pwd_btn is not None:
            self.toggle_pwd_btn.clicked.connect(self.toggle_password)

    # Defining the functions
    def toggle_password(self):
        if self.pwd_input is None:
            return
        if self.password_visible:
            self.pwd_input.setEchoMode(QLineEdit.Password)
            self.password_visible = False
        else:
            self.pwd_input.setEchoMode(QLineEdit.Normal)
            self.password_visible = True

    def handle_login(self):
        if self.username_input is None or self.pwd_input is None:
            self.show_error("Login form is missing required fields.")
            return
        username = self.username_input.text().strip()
        password = self.pwd_input.text().strip()

        if username == "" or password == "":
            self.show_error("Please fill in all fields.")
            return

        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE Username = ? AND Password = ?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user is None:
            self.show_error("Invalid username or password.")
            return

        role = str(user[3]).strip().lower()
        normalized_role = role.replace(" ", "").replace("_", "")

        if normalized_role == "superadmin":
            self.open_super_admin(user)
        elif normalized_role == "admin":
            self.open_admin_dashboard(user)
        elif normalized_role == "student":
            self.open_student_dashboard(user)
        else:
            self.show_error("Unknown user role.")

    def set_role(self, role):
        self.selected_role = role

    def show_error(self, message):
        if self.error_label is not None:
            self.error_label.setText(message)
            self.error_label.show()

    def open_super_admin(self, user):
        from windows.super_admin import SuperAdminDashboard
        self.window = SuperAdminDashboard(user)
        self.window.show()
        self.close()

    def open_admin_dashboard(self, user):
        from windows.admin_dashboard import AdminDashboard
        self.admin = AdminDashboard(user)
        self.admin.show()
        self.close()

    def open_student_dashboard(self, user):
        from windows.student_dashboard import StudentDashboard
        self.student = StudentDashboard(user)
        self.student.show()
        self.close()

