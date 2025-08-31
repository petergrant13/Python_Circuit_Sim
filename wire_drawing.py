# wire_drawing.py
from PySide6.QtWidgets import QGraphicsScene, QGraphicsLineItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QColor

# Globals
TERMINAL_SNAP_DISTANCE = 10  # pixels


class WireSegment(QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)
        # Consistent wire styling
        self.normal_pen = QPen(Qt.black, 2)
        self.selected_pen = QPen(Qt.blue, 2)
        self.setPen(self.normal_pen)
        self.setFlags(QGraphicsLineItem.ItemIsSelectable)

    def paint(self, painter, option, widget=None):
        self.setPen(self.selected_pen if self.isSelected() else self.normal_pen)
        super().paint(painter, option, widget)


class CircuitScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.wire_mode = False
        self.start_point = None
        self.preview_line1 = None
        self.preview_line2 = None
        self.node_manager = NodeManager()

    def find_near_terminal(self, point: QPointF):
        for item in self.items():
            if hasattr(item, "terminals"):
                for terminal in item.terminals():
                    if (terminal - point).manhattanLength() <= TERMINAL_SNAP_DISTANCE:
                        return terminal
        return None

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

    # Draw orthogonal (L-shaped) wire(s), with snapping
    def draw_L_wire(self, start, end, threshold=5):
        # Snap start and end to nearby terminals if close
        start_snap = self.find_near_terminal(start) or start
        end_snap = self.find_near_terminal(end) or end

        dx = abs(start_snap.x() - end_snap.x())
        dy = abs(start_snap.y() - end_snap.y())

        if dx < threshold:
            self._add_wire_segment(start_snap, QPointF(start_snap.x(), end_snap.y()))
        elif dy < threshold:
            self._add_wire_segment(start_snap, QPointF(end_snap.x(), start_snap.y()))
        else:
            mid1 = QPointF(end_snap.x(), start_snap.y())
            mid2 = QPointF(start_snap.x(), end_snap.y())

            if (start_snap - mid1).manhattanLength() + (mid1 - end_snap).manhattanLength() < \
               (start_snap - mid2).manhattanLength() + (mid2 - end_snap).manhattanLength():
                self._add_wire_segment(start_snap, mid1)
                self._add_wire_segment(mid1, end_snap)
            else:
                self._add_wire_segment(start_snap, mid2)
                self._add_wire_segment(mid2, end_snap)

        # Connect endpoints to nodes (backend)
        for point in (start_snap, end_snap):
            for item in self.items():
                if hasattr(item, "terminals"):
                    for i, terminal in enumerate(item.terminals()):
                        if (terminal - point).manhattanLength() <= TERMINAL_SNAP_DISTANCE:
                            self.node_manager.connect_terminal(item, i, terminal)

    def _add_wire_segment(self, p1, p2):
        line = WireSegment(p1.x(), p1.y(), p2.x(), p2.y())
        self.addItem(line)

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


class Node:
    def __init__(self):
        self.points: list[QPointF] = []
        self.components: list[tuple[object, int]] = []  # (component, terminal_index)
        self.id: int = -1
        self.is_ground: bool = False

    def add_terminal(self, point: QPointF, component, terminal_index: int):
        self.points.append(point)
        self.components.append((component, terminal_index))

    def __repr__(self):
        return f"<Node id={self.id} ground={self.is_ground} : {len(self.points)} points, {len(self.components)} connections>"


class NodeManager:
    def __init__(self):
        self.nodes: list[Node] = []

    def find_or_create_node(self, point: QPointF, threshold=10):
        for node in self.nodes:
            for p in node.points:
                if (p - point).manhattanLength() <= threshold:
                    return node
        node = Node()
        self.nodes.append(node)
        return node

    def connect_terminal(self, component, terminal_index: int, terminal_pos: QPointF):
        node = self.find_or_create_node(terminal_pos)
        node.add_terminal(terminal_pos, component, terminal_index)

    def finalize_nodes(self):
        # Determine ground membership per node without importing component types
        for node in self.nodes:
            node.is_ground = any(getattr(c, "is_ground_symbol", False) for (c, _) in node.components)

        ground_nodes = [n for n in self.nodes if n.is_ground]
        if not ground_nodes:
            print("Error: No ground node found.")
            # Assign incremental IDs anyway
            for i, n in enumerate(self.nodes):
                n.id = i
            return

        # Put the first ground node at id 0, others after
        ground_node = ground_nodes[0]
        ordered = [ground_node] + [n for n in self.nodes if n is not ground_node]
        for i, n in enumerate(ordered):
            n.id = i
        self.nodes = ordered
