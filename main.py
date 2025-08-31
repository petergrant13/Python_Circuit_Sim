# main.py
import sys
from PySide6.QtWidgets import QApplication
from gui import CircuitWindow


def main():
    app = QApplication(sys.argv)
    window = CircuitWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
