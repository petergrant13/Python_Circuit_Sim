# This file will handle the gui with PySide6
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QMainWindow
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt

from components import ResistorSymbol


class CircuitWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Circuit Simulator")
        self.setGeometry(100, 100, 800, 600)

        # Set up the scene and view
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-400, -300, 800, 600)
        self.view = QGraphicsView(self.scene)
        self.view.setBackgroundBrush(Qt.white)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(self.view)

        # Add a resistor symbol to the scene
        resistor = ResistorSymbol()
        self.scene.addItem(resistor)
        resistor.setPos(0, 0)

