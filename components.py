# This file has all the component class creators

from PySide6.QtWidgets import QGraphicsTextItem, QGraphicsItem, QInputDialog, QGraphicsLineItem
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
        # Default to horizontal layout — override if needed
        pos = self.scenePos()
        dx = 30
        return [pos + QPointF(-dx, 0), pos + QPointF(dx, 0)]


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

class Wire(QGraphicsLineItem):
    def __init__(self, start_item, end_item=None):
        super().__init__()
        self.setPen(QPen(Qt.black, 2))
        self.start_item = start_item
        self.end_item = end_item
        self.start_terminal = None        # Point on start component
        self.floating_end_pos = None      # Only used during dragging
        self.setZValue(-1)
        self.update_position()

    def update_position(self):
        if self.start_item:
            p1 = self.start_terminal or self.start_item.terminals()[1]
            if self.end_item:
                p2 = self.end_item.terminals()[0]
            elif self.floating_end_pos:
                p2 = self.floating_end_pos
            else:
                return  # Can't draw line
            self.setLine(p1.x(), p1.y(), p2.x(), p2.y())


class Node:
    def __init__(self, position: QPointF):
        self.position = position
        self.connected_components = []

    def connect(self, component):
        if component not in self.connected_components:
            self.connected_components.append(component)

    def __repr__(self):
        return f"Node(pos={self.position}, components={[c.label for c in self.connected_components]})"

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