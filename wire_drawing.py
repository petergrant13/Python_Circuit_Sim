# wire_drawing.py
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QColor


class CircuitScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.wire_mode = False
        self.start_point = None
        self.preview_line1 = None
        self.preview_line2 = None

    def set_wire_mode(self, enabled: bool):
        self.wire_mode = enabled
        if not enabled:
            self.start_point = None
            self.remove_preview()

    def mousePressEvent(self, event):
        if not self.wire_mode:
            return super().mousePressEvent(event)

        point = event.scenePos()
        if self.start_point is None:
            self.start_point = point
        else:
            self.draw_L_wire(self.start_point, point)
            self.start_point = None
            self.remove_preview()

    def mouseMoveEvent(self, event):
        if self.wire_mode and self.start_point:
            self.update_preview(self.start_point, event.scenePos())
        else:
            super().mouseMoveEvent(event)

    def draw_L_wire(self, start, end):
        mid1 = QPointF(end.x(), start.y())
        mid2 = QPointF(start.x(), end.y())

        if (start - mid1).manhattanLength() + (mid1 - end).manhattanLength() < \
           (start - mid2).manhattanLength() + (mid2 - end).manhattanLength():
            self.addLine(start.x(), start.y(), mid1.x(), mid1.y(), QPen(Qt.black, 2))
            self.addLine(mid1.x(), mid1.y(), end.x(), end.y(), QPen(Qt.black, 2))
        else:
            self.addLine(start.x(), start.y(), mid2.x(), mid2.y(), QPen(Qt.black, 2))
            self.addLine(mid2.x(), mid2.y(), end.x(), end.y(), QPen(Qt.black, 2))

    def update_preview(self, start, current):
        self.remove_preview()

        mid1 = QPointF(current.x(), start.y())
        mid2 = QPointF(start.x(), current.y())

        if (start - mid1).manhattanLength() + (mid1 - current).manhattanLength() < \
           (start - mid2).manhattanLength() + (mid2 - current).manhattanLength():
            p1, p2 = (start, mid1), (mid1, current)
        else:
            p1, p2 = (start, mid2), (mid2, current)

        pen = QPen(QColor("gray"), 1, Qt.DashLine)
        self.preview_line1 = self.addLine(p1[0].x(), p1[0].y(), p1[1].x(), p1[1].y(), pen)
        self.preview_line2 = self.addLine(p2[0].x(), p2[0].y(), p2[1].x(), p2[1].y(), pen)

    def remove_preview(self):
        if self.preview_line1:
            self.removeItem(self.preview_line1)
            self.preview_line1 = None
        if self.preview_line2:
            self.removeItem(self.preview_line2)
            self.preview_line2 = None
