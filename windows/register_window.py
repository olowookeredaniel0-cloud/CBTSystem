from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import os
import re

# Creating the class RegisterWindow
class RegisterWindow(QDialog):
    def __init__(self, parent=None):
        super(RegisterWindow, self).__init__(parent)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "CBTRegPage.ui")
        loadUi(ui_path, self)
        self.name_input = self.findChild(QLineEdit, "name_input")
        self.email_input = self.findChild(QLineEdit, "email_input")
        self.pwd_input = self.findChild(QLineEdit, "pwd_input")
        self.register_btn = self.findChild(QPushButton, "register_btn")
        self.back_btn = self.findChild(QPushButton, "back_btn")
        self.toggle_pwd_btn = self.findChild(QPushButton, "toggle_pwd_btn")
        self.error_label = self.findChild(QLabel, "error_label")
        self.success_label = self.findChild(QLabel, "success_label")


        # Hiding the labels
        if self.error_label is not None:
            self.error_label.hide()
        if self.success_label is not None:
            self.success_label.hide()


        # Hiding the password
        if self.pwd_input is not None:
            self.pwd_input.setEchoMode(QLineEdit.Password)
        self.password_visible = False


        # Connecting the buttons
        if self.register_btn is not None:
            self.register_btn.clicked.connect(self.handle_register)
        if self.back_btn is not None:
            self.back_btn.clicked.connect(self.go_back)
        if self.toggle_pwd_btn is not None:
            self.toggle_pwd_btn.clicked.connect(self.toggle_password)


    def toggle_password(self):
        if self.pwd_input is None:
            return
        if self.password_visible:
            self.pwd_input.setEchoMode(QLineEdit.Password)
            self.password_visible = False
        else:
            self.pwd_input.setEchoMode(QLineEdit.Normal)
            self.password_visible = True

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

    def handle_register(self):
        if self.name_input is None or self.pwd_input is None:
            self.show_error("Registration form is missing required fields.")
            return

        username = self.name_input.text().strip()
        password = self.pwd_input.text().strip()

        # Empty field check
        if not username or not password:
            self.show_error("Please fill in all fields.")
            return

        # Username format check
        username_regex = r"^[A-Za-z0-9_]{3,30}$"
        if not re.match(username_regex, username):
            self.show_error("Username must be 3-30 chars (letters, numbers, underscore).")
            return

        # Password strength check
        password_regex = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$"
        if not re.match(password_regex, password):
            self.show_error("Password must have uppercase, lowercase, a number and be at least 8 characters.")
            self.pwd_input.clear()
            return

        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()

        # Duplicate username check
        cur.execute("SELECT ID FROM Users WHERE Username = ?", (username,))
        if cur.fetchone():
            self.show_error("That username is already taken.")
            conn.close()
            return

        # Insert new student
        cur.execute(
            "INSERT INTO Users (Username, Password, Role) VALUES (?, ?, ?)",
            (username, password, "student")
        )
        conn.commit()
        conn.close()

        self.show_success("Account created successfully! Please log in.")
        self.go_back()

    def go_back(self):
        from windows.login_window import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()