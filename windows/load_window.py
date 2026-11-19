from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
import os


# Creating the class LoadWindow
class LoadWindow(QDialog):
    def __init__(self, parent=None):
        super(LoadWindow, self).__init__(parent)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        ui_path = os.path.join(base_dir, "ui", "CBTLoadApp.ui")
        loadUi(ui_path, self)
        self.progress_bar = self.findChild(QProgressBar, "progress_bar") or self.findChild(QProgressBar, "load_progressbar")
        self.status_label = self.findChild(QLabel, "status_label")

        # Initial values
        self.progress_value = 0
        self.opening_login = False

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)

    # Defining the functions
    def update_progress(self):
        if self.opening_login:
            return
        self.progress_value += 20
        if self.progress_bar is not None:
            self.progress_bar.setValue(self.progress_value)

        # Status Update
        if self.progress_value < 30:
            if self.status_label is not None:
                self.status_label.setText("Initializing...")
        elif self.progress_value < 70:
            if self.status_label is not None:
                self.status_label.setText("Loading resources...")
        elif self.progress_value < 100:
            if self.status_label is not None:
                self.status_label.setText("Starting application...")

        # When loading finishes
        if self.progress_value >= 100:
            self.timer.stop()
            self.opening_login = True
            self.open_login()

    def open_login(self):
        from windows.login_window import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        # Keep splash instance alive during handoff to avoid Qt object lifetime issues.
        self.hide()

    def closeEvent(self, event):
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()
        super(LoadWindow, self).closeEvent(event)