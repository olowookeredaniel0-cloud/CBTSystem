from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import os

# Creating the class AdminDashboard
class AdminDashboard(QDialog):
    def __init__(self, user, parent=None):
        super(AdminDashboard, self).__init__(parent)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "CBTAdminDash.ui")
        loadUi(ui_path, self)
        self.user = user
        self.welcomeLabel = self.findChild(QLabel, "welcomeLabel") or self.findChild(QLabel, "adminTitleLabel")
        self.adminSubLabel = self.findChild(QLabel, "adminSubLabel") or self.findChild(QLabel, "subtitleLabel")
        self.view_results_btn = self.findChild(QPushButton, "view_results_btn")
        self.manage_subjects_btn = self.findChild(QPushButton, "manage_subjects_btn")
        self.logout_btn = self.findChild(QPushButton, "logout_btn")
        self.error_label = self.findChild(QLabel, "error_label")
        self.success_label = self.findChild(QLabel, "success_label")

        # Hiding the message labels
        if self.error_label is not None:
            self.error_label.hide()
        if self.success_label is not None:
            self.success_label.hide()

        # Showing admin name
        username = self._get_username()
        if self.welcomeLabel is not None:
            self.welcomeLabel.setText(f"Welcome, {username}")
        if self.adminSubLabel is not None:
            self.adminSubLabel.setText("Admin Panel")

        # Connecting the buttons
        if self.view_results_btn is not None:
            self.view_results_btn.clicked.connect(self.open_view_results)
        if self.manage_subjects_btn is not None:
            self.manage_subjects_btn.clicked.connect(self.open_manage_subjects)
        if self.logout_btn is not None:
            self.logout_btn.clicked.connect(self.logout)

    # Defining the functions
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

    def open_view_results(self):
        from windows.view_result import ViewResult
        self.view_r = ViewResult(self.user)
        self.view_r.show()
        self.close()

    def open_manage_subjects(self):
        from windows.manage_subjects import ManageSubjects
        self.manage_subjects = ManageSubjects(self.user)
        self.manage_subjects.show()
        self.close()

    def logout(self):
        from windows.login_window import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()

    def _get_username(self):
        if not self.user:
            return "User"
        if isinstance(self.user, dict):
            return str(self.user.get("Username") or self.user.get("username") or "User")
        try:
            return str(self.user[1]) if self.user[1] else "User"
        except Exception:
            return "User"