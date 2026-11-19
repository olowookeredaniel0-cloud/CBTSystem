import sys
from PyQt5.QtWidgets import QApplication
from windows.load_window import LoadWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoadWindow()
    window.show()
    sys.exit(app.exec_())