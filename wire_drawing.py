# This has a bunch of stuff to handle drawing wires and making connections

from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import Qt, QPointF
from components import CircuitComponent, Node, Wire


class CircuitScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.drawing_wire = False
        self.temp_wire = None
        self.start_item = None
        self.start_terminal = None
        self.nodes = []

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            clicked_pos = event.scenePos()
            comp, terminal = self.find_terminal_near(clicked_pos)
            if comp:
                self.start_item = comp
                self.start_terminal = terminal
                self.temp_wire = Wire(comp)
                self.temp_wire.start_terminal = terminal
                self.temp_wire.floating_end_pos = terminal
                self.temp_wire.update_position()
                self.addItem(self.temp_wire)
                self.drawing_wire = True
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing_wire and self.temp_wire:
            line = self.temp_wire.line()
            self.temp_wire.setLine(
                line.x1(), line.y1(),
                event.scenePos().x(), event.scenePos().y()
            )
            self.temp_wire.floating_end_pos = event.scenePos()
            self.temp_wire.update_position()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drawing_wire and self.start_item:
            comp, terminal = self.find_terminal_near(event.scenePos())
            if comp and comp != self.start_item:
                # Complete the wire
                wire = Wire(self.start_item, comp)
                wire.start_terminal = self.start_terminal
                wire.update_position()
                self.addItem(wire)


                # Create or use existing nodes
                node_start = self.get_or_create_node(self.start_terminal)
                node_end = self.get_or_create_node(terminal)

                node_start.connect(self.start_item)
                node_end.connect(comp)
            if self.temp_wire:
                self.removeItem(self.temp_wire)
            self.reset_wire_drawing()
        else:
            super().mouseReleaseEvent(event)

    def reset_wire_drawing(self):
        self.drawing_wire = False
        self.temp_wire = None
        self.start_item = None
        self.start_terminal = None

    def find_terminal_near(self, pos: QPointF, threshold=10) -> tuple[CircuitComponent, QPointF] | tuple[None, None]:
        for item in self.items(pos):
            if isinstance(item, CircuitComponent):
                for term in item.terminals():
                    if (term - pos).manhattanLength() < threshold:
                        return item, term
        return None, None

    def get_or_create_node(self, pos: QPointF) -> Node:
        for node in self.nodes:
            if (node.position - pos).manhattanLength() < 5:
                return node
        new_node = Node(pos)
        self.nodes.append(new_node)
        return new_node
