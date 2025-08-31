from PySide6.QtWidgets import (
    QGraphicsView, QMainWindow,
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout,
    QGraphicsLineItem, QMessageBox, QToolBar
)
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt
from wire_drawing import CircuitScene
from components import ResistorSymbol, VoltageSourceSymbol, GroundSymbol
from solver import CircuitSolver


class CircuitWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Circuit Simulator")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        layout_buttons = QHBoxLayout()
        self.setCentralWidget(central_widget)

        # Toolbar (create it!)
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Scene and view
        self.scene = CircuitScene()
        self.scene.setSceneRect(-400, -300, 800, 600)
        self.view = QGraphicsView(self.scene)
        self.view.setBackgroundBrush(Qt.white)
        self.view.setRenderHint(QPainter.Antialiasing)

        # Counters
        self.resistor_count = 0
        self.voltage_count = 0

        # Buttons
        toggle_wire_button = QPushButton("Draw Wire")
        toggle_wire_button.setCheckable(True)
        toggle_wire_button.toggled.connect(self.toggle_wire_mode)
        layout_buttons.addWidget(toggle_wire_button)

        add_resistor_button = QPushButton("Add Resistor")
        add_resistor_button.clicked.connect(self.add_resistor)

        add_voltage_button = QPushButton("Add Voltage Source")
        add_voltage_button.clicked.connect(self.add_voltage_source)

        add_ground_button = QPushButton("Add GND")
        add_ground_button.clicked.connect(self.add_ground)

        check_button = QPushButton("Check Circuit")
        check_button.clicked.connect(self.check_circuit)

        # ✅ Solve button goes in the toolbar
        solve_button = QPushButton("Solve Circuit")
        solve_button.clicked.connect(self.solve_circuit)
        toolbar.addWidget(solve_button)

        # Layout
        main_layout.addWidget(self.view)
        main_layout.addLayout(layout_buttons)
        layout_buttons.addWidget(add_resistor_button)
        layout_buttons.addWidget(add_voltage_button)
        layout_buttons.addWidget(add_ground_button)
        layout_buttons.addWidget(check_button)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R:
            for item in self.scene.selectedItems():
                if hasattr(item, "rotate"):
                    item.rotate()
        elif event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            for item in self.scene.selectedItems():
                if isinstance(item, QGraphicsLineItem):
                    self.scene.removeItem(item)

    def toggle_wire_mode(self, checked):
        self.scene.set_wire_mode(checked)

    def add_ground(self):
        ground = GroundSymbol()
        ground.setPos(0, 100)
        self.scene.addItem(ground)

    def add_resistor(self):
        self.resistor_count += 1
        label = f"R{self.resistor_count}"
        resistance = 100
        resistor = ResistorSymbol(label, resistance)
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

        self.scene.node_manager.finalize_nodes()
        print("== Nodes ==")
        for node in self.scene.node_manager.nodes:
            print(node)

    def solve_circuit(self):
        self.scene.node_manager.finalize_nodes()

        # Collect components
        components = []
        for item in self.scene.items():
            if isinstance(item, (ResistorSymbol, VoltageSourceSymbol)):
                components.append(item)

        # Use solver
        try:
            solver = CircuitSolver(components, self.scene.node_manager.nodes)
            node_voltages, branch_currents = solver.solve()

            msg = "Node Voltages:\n"
            for nid, v in node_voltages.items():
                msg += f"  Node {nid}: {v:.3f} V\n"
            msg += "\nBranch Currents:\n"
            for name, i in branch_currents.items():
                msg += f"  {name}: {i:.3f} A\n"

            QMessageBox.information(self, "Circuit Solution", msg)

        except Exception as e:
            QMessageBox.critical(self, "Solve Error", str(e))
