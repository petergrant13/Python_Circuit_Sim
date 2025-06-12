# This file will handle the gui with PySide6
from PySide6.QtWidgets import QApplication, QLabel

app = QApplication([])
label = QLabel("Hello from PySide6!")
label.show()
app.exec()
