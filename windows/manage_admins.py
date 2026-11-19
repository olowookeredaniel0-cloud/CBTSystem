from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import os


class ManageAdmins(QDialog):
    def __init__(self, user, parent=None):
        super(ManageAdmins, self).__init__(parent)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "CBTManageAdmins.ui")
        loadUi(ui_path, self)
        self.user = user
        self.username_input = self.findChild(QLineEdit, "username_input")
        self.pwd_input = self.findChild(QLineEdit, "pwd_input")
        self.add_admin_btn = self.findChild(QPushButton, "add_admin_btn")
        self.admins_table = self.findChild(QTableWidget, "admins_table")
        self.delete_btn = self.findChild(QPushButton, "delete_btn")
        self.back_btn = self.findChild(QPushButton, "back_btn")
        self.error_label = self.findChild(QLabel, "error_label")
        self.success_label = self.findChild(QLabel, "success_label")

        if self.error_label is not None:
            self.error_label.hide()
        if self.success_label is not None:
            self.success_label.hide()

        # Set up table
        if self.admins_table is not None:
            self.admins_table.setColumnCount(3)
            self.admins_table.setHorizontalHeaderLabels(["ID", "Username", "Role"])
            self.admins_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.admins_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.admins_table.setSelectionBehavior(QTableWidget.SelectRows)

        self.load_admins()

        if self.add_admin_btn is not None:
            self.add_admin_btn.clicked.connect(self.add_admin)
        if self.delete_btn is not None:
            self.delete_btn.clicked.connect(self.delete_admin)
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

    def load_admins(self):
        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT ID, Username, Role FROM Users WHERE LOWER(REPLACE(Role, ' ', '')) = 'admin'")
        rows = cur.fetchall()
        conn.close()

        if self.admins_table is None:
            return
        self.admins_table.setRowCount(0)
        for row_data in rows:
            row = self.admins_table.rowCount()
            self.admins_table.insertRow(row)
            for col, val in enumerate(row_data):
                self.admins_table.setItem(row, col, QTableWidgetItem(str(val)))

    def add_admin(self):
        if self.username_input is None or self.pwd_input is None:
            self.show_error("Admin form is missing required fields.")
            return
        username = self.username_input.text().strip()
        password = self.pwd_input.text().strip()

        if not username or not password:
            self.show_error("Please fill in username and password.")
            return

        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()

        # Check duplicate username
        cur.execute("SELECT ID FROM Users WHERE Username = ?", (username,))
        if cur.fetchone():
            self.show_error("Username already exists.")
            conn.close()
            return

        cur.execute(
            "INSERT INTO Users (Username, Password, Role, CreatedBy) VALUES (?, ?, 'Admin', ?)",
            (username, password, self.user[0])
        )
        conn.commit()
        conn.close()

        self.show_success(f"Admin '{username}' created successfully.")
        self.username_input.clear()
        self.pwd_input.clear()
        self.load_admins()

    def delete_admin(self):
        if self.admins_table is None:
            self.show_error("Admins table is missing from this UI.")
            return
        selected = self.admins_table.currentRow()
        if selected < 0:
            self.show_error("Please select an admin to delete.")
            return

        # Get admin ID from first column
        admin_id = self.admins_table.item(selected, 0).text()
        admin_name = self.admins_table.item(selected, 1).text()

        from database import create_connection
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM Users WHERE ID = ?", (admin_id,))
        conn.commit()
        conn.close()

        self.show_success(f"Admin '{admin_name}' deleted.")
        self.load_admins()

    def go_back(self):
        from windows.super_admin import SuperAdminDashboard
        self.window = SuperAdminDashboard(self.user)
        self.window.show()
        self.close()