# This file has all the component class creators

from PySide6.QtWidgets import QGraphicsTextItem, QGraphicsItem, QInputDialog, QGraphicsLineItem, QMainWindow
from PySide6.QtGui import QPainter, QPen, QFont
from PySide6.QtCore import QRectF, Qt, QPointF


class CircuitComponent(QGraphicsItem):
    def __init__(self, label="?", value=0, value_unit=""):
        super().__init__()
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable
        )
        self.rotation_angle = 0
        self.label = label
        self.value = value
        self.value_unit = value_unit

        font = QFont("Arial", 10)
        self.text_item = QGraphicsTextItem(self.label_text(), self)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(Qt.darkBlue)
        self.text_item.setPos(-20, -40)
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)

    def terminals(self) -> list[QPointF]:
        # Define terminals in local coordinates
        local_terminals = [QPointF(-30, 0), QPointF(30, 0)]  # override per component as needed
        return [self.mapToScene(p) for p in local_terminals]


    def label_text(self):
        return f"{self.label} {self.value}{self.value_unit}"

    def rotate(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.setRotation(self.rotation_angle)

    def mouseDoubleClickEvent(self, event):
        new_label, ok1 = QInputDialog.getText(None, "Edit Label", "New Label:", text=self.label)
        new_value, ok2 = QInputDialog.getDouble(None, f"Edit {self.value_unit}", f"Value ({self.value_unit}):", value=self.value, decimals=2)

        if ok1 and ok2:
            self.update_label(new_label, new_value)

    def update_label(self, new_label, new_value):
        self.label = new_label
        self.value = new_value
        self.text_item.setPlainText(self.label_text())


class GroundSymbol(CircuitComponent):
    def __init__(self, label="GND"):
        super().__init__(label, 0, "")
        self.text_item.setVisible(False) 

    def boundingRect(self):
        return QRectF(-10, -10, 20, 20)

    def paint(self, painter, option, widget=None):
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)

        # Vertical line
        painter.drawLine(0, -10, 0, 0)
        # Three horizontal lines
        painter.drawLine(-6, 0, 6, 0)
        painter.drawLine(-4, 3, 4, 3)
        painter.drawLine(-2, 6, 2, 6)

    def terminals(self) -> list[QPointF]:
        return [self.scenePos() + QPointF(0, -10)]
    

class ResistorSymbol(CircuitComponent):
    def __init__(self, label="R1", resistance=100):
        super().__init__(label, resistance, "Ω")

    def boundingRect(self):
        return QRectF(-30, -10, 60, 20)

    def paint(self, painter, option, widget=None):
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)

        # Draw horizontal lines before/after the zigzag
        painter.drawLine(-30, 0, -15, 0)
        painter.drawLine(15, 0, 30, 0)

        # Draw zigzag
        zigzag_points = [
            (-15, 0), (-12, -10), (-9, 10), (-6, -10),
            (-3, 10), (0, -10), (3, 10), (6, -10),
            (9, 10), (12, -10), (15, 0)
        ]

        for i in range(len(zigzag_points) - 1):
            start = zigzag_points[i]
            end = zigzag_points[i + 1]
            painter.drawLine(*start, *end)


class VoltageSourceSymbol(CircuitComponent):
    def __init__(self, label="V1", voltage=5):
        super().__init__(label, voltage, "V")

    def boundingRect(self):
        return QRectF(-20, -40, 40, 80)
    
    def paint(self, painter, option, widget=None):
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)

        # Vertical wires
        painter.drawLine(0, -40, 0, -20)
        painter.drawLine(0, 20, 0, 40)

        # Circle for the voltage source body
        painter.drawEllipse(-20, -20, 40, 40)

        # Plus and minus signs
        painter.setFont(self.text_item.font())
        painter.drawText(-3, -10, "+")
        painter.drawText(-3, 10, "−")