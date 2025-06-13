from PySide6.QtWidgets import (
    QGraphicsScene, QGraphicsView, QMainWindow,
    QPushButton, QWidget, QVBoxLayout
)
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt

from components import ResistorSymbol, VoltageSourceSymbol


class CircuitWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Circuit Simulator")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Set up the scene and view
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-400, -300, 800, 600)
        self.view = QGraphicsView(self.scene)
        self.view.setBackgroundBrush(Qt.white)
        self.view.setRenderHint(QPainter.Antialiasing)

        # Add an initial resistor symbol to the scene
        self.resistor_count = 1
        resistor = ResistorSymbol(f"R{self.resistor_count}", 100)
        self.scene.addItem(resistor)
        resistor.setPos(0, 0)

        # Initialize voltage source count
        self.voltage_count = 0

        # Buttons
        add_resistor_button = QPushButton("Add Resistor")
        add_resistor_button.clicked.connect(self.add_resistor)

        add_voltage_button = QPushButton("Add Voltage Source")
        add_voltage_button.clicked.connect(self.add_voltage_source)

        check_button = QPushButton("Check Circuit")
        check_button.clicked.connect(self.check_circuit)

        # Add widgets to layout
        layout.addWidget(self.view)
        layout.addWidget(add_resistor_button)
        layout.addWidget(add_voltage_button)
        layout.addWidget(check_button)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R:
            for item in self.scene.selectedItems():
                if hasattr(item, "rotate"):
                    item.rotate()

    def add_resistor(self):
        self.resistor_count += 1
        label = f"R{self.resistor_count}"
        resistance = 100
        resistor = ResistorSymbol(label, resistance)
        # Position new resistor with some spacing
        resistor.setPos(-100 + 40 * self.resistor_count, -100)
        self.scene.addItem(resistor)

    def add_voltage_source(self):
        self.voltage_count += 1
        label = f"V{self.voltage_count}"
        voltage = 5
        voltage_source = VoltageSourceSymbol(label, voltage)
        voltage_source.setPos(-100 + 40 * self.voltage_count, 0)
        self.scene.addItem(voltage_source)

    def check_circuit(self):
        print("Current Circuit Components:")
        for item in self.scene.items():
            if isinstance(item, ResistorSymbol):
                print(f"Resistor: Label={item.label}, Resistance={item.value}Ω")
            elif isinstance(item, VoltageSourceSymbol):
                print(f"Voltage Source: Label={item.label}, Voltage={item.value}V")
