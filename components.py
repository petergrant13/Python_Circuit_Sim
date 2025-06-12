# This file will have component info
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import QRectF, Qt


class ResistorSymbol(QGraphicsItem):
    def boundingRect(self):
        return QRectF(-30, -10, 60, 20)

    def paint(self, painter, option, widget=None):
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)

        # Draw horizontal lines before/after the zigzag
        painter.drawLine(-30, 0, -15, 0)
        painter.drawLine(15, 0, 30, 0)

        # Draw zigzag (resistor)
        zigzag_points = [
            (-15, 0), (-12, -10), (-9, 10), (-6, -10),
            (-3, 10), (0, -10), (3, 10), (6, -10),
            (9, 10), (12, -10), (15, 0)
        ]

        for i in range(len(zigzag_points) - 1):
            start = zigzag_points[i]
            end = zigzag_points[i + 1]
            painter.drawLine(*start, *end)
