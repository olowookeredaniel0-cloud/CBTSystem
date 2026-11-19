import os
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtGui import QColor

# Creating the class ViewResult
class ViewResult(QDialog):
    def __init__(self, user, parent=None):
        super(ViewResult, self).__init__(parent)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "CBTViewResults.ui")
        loadUi(ui_path, self)
        self.user = user
        self.results_table = self.findChild(QTableWidget, "results_table")
        self.search_input = self.findChild(QLineEdit, "search_input")
        self.back_btn = self.findChild(QPushButton, "back_btn")
        self.error_label = self.findChild(QLabel, "error_label")
        self.success_label = self.findChild(QLabel, "success_label")

        if self.results_table is None:
            raise RuntimeError("CBTViewResults.ui did not load correctly (missing results_table).")

        # Hiding the message labels
        if self.error_label is not None:
            self.error_label.hide()
        if self.success_label is not None:
            self.success_label.hide()

        # The table columns
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(
            ["Student Name", "Subject", "Score", "Total", "Date", "Status"]
        )

        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.load_results()

        # Connecting the buttons and search_input
        if self.back_btn is not None:
            self.back_btn.clicked.connect(self.go_back)
        if self.search_input is not None:
            self.search_input.textChanged.connect(self.search_results)

    # Defining the functions
    def show_error(self, message):
        self.success_label.hide()
        self.error_label.setText(message)
        self.error_label.show()

    def show_success(self, message):
        self.error_label.hide()
        self.success_label.setText("Your latest result has been loaded.")
        self.success_label.show()

    def load_results(self, filter_text=""):
        from database import create_connection
        try:
            conn = create_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT Users.Username, Subjects.Name, Results.Score, Results.TotalQuestions, Results.Date
                FROM Results
                JOIN Users ON Results.StudentID = Users.ID
                JOIN Quizzes ON Results.QuizID = Quizzes.ID
                JOIN Subjects ON Quizzes.SubjectID = Subjects.ID
                ORDER BY Results.ID DESC
                """
            )
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            self.show_error(f"Could not load results: {e}")
            return

        # Filtering the rows
        if filter_text:
            query = filter_text.lower()
            rows = [
                r for r in rows
                if query in str(r[0]).lower() or query in str(r[1]).lower()
            ]

        # Clearing the existing table content
        self.results_table.setRowCount(0)

        if not rows:
            self.show_error("No results found.")
            return
        self.error_label.hide()

        # Filling table row by row
        for row_data in rows:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)

            name, subject, score, total, date = row_data
            total_val = total if total is not None else 0
            score_val = score if score is not None else 0
            percent = int((score_val / total_val) * 100) if total_val > 0 else 0
            status = "Pass" if percent >= 50 else "Fail"

            self.results_table.setItem(row, 0, QTableWidgetItem(str(name)))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(subject)))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(score)))
            self.results_table.setItem(row, 3, QTableWidgetItem(str(total)))
            self.results_table.setItem(row, 4, QTableWidgetItem(str(date)))

            # Colour the status cells: Green(Pass), Red(Fail)
            status_item = QTableWidgetItem(status)
            if status == "Pass":
                status_item.setForeground(QColor("#6FCF6F"))
            else:
                status_item.setForeground(QColor("#CF6F6F"))
            self.results_table.setItem(row, 5, status_item)

    def search_results(self):
        self.load_results(filter_text=self.search_input.text().strip())

    def go_back(self):
        from windows.admin_dashboard import AdminDashboard
        self.admin = AdminDashboard(self.user)
        self.admin.show()
        self.close()