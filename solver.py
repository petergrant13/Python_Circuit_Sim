import numpy as np

class CircuitSolver:
    def __init__(self, components, nodes):
        self.components = components
        self.nodes = nodes
        self.ground_node = self.find_ground_node()

    def find_ground_node(self):
        for node in self.nodes:
            if getattr(node, "ground", False) or node.id == 0:
                return node
        raise ValueError("No ground node found!")


    def solve(self):
        # Map node IDs to matrix indices (excluding ground)
        node_ids = [n.id for n in self.nodes if n is not self.ground_node]
        id_to_index = {nid: i for i, nid in enumerate(node_ids)}

        n = len(node_ids)
        G = np.zeros((n, n))  # conductance matrix
        I = np.zeros(n)       # current sources

        branch_currents = {}

        for comp in self.components:
            if hasattr(comp, "value") and comp.label.startswith("R"):
                # Resistor
                n1, n2 = comp.node_ids  # store this when adding to NodeManager
                g = 1.0 / comp.value
                if n1 != self.ground_node.id:
                    i = id_to_index[n1]
                    G[i, i] += g
                if n2 != self.ground_node.id:
                    j = id_to_index[n2]
                    G[j, j] += g
                if n1 != self.ground_node.id and n2 != self.ground_node.id:
                    i, j = id_to_index[n1], id_to_index[n2]
                    G[i, j] -= g
                    G[j, i] -= g

            elif hasattr(comp, "value") and comp.label.startswith("V"):
                # For now only handle voltage source to ground
                n1, n2 = comp.node_ids
                if n2 == self.ground_node.id:
                    if n1 != self.ground_node.id:
                        i = id_to_index[n1]
                        I[i] += comp.value / 1e-12  # hack: treat as current injection
                elif n1 == self.ground_node.id:
                    if n2 != self.ground_node.id:
                        j = id_to_index[n2]
                        I[j] -= comp.value / 1e-12
                else:
                    raise NotImplementedError("Voltage sources between two non-ground nodes not handled yet")

        # Solve for voltages
        V = np.linalg.solve(G, I)

        node_voltages = {self.ground_node.id: 0.0}
        for nid, idx in id_to_index.items():
            node_voltages[nid] = V[idx]

        # Compute branch currents (resistors only for now)
        for comp in self.components:
            if comp.label.startswith("R"):
                n1, n2 = comp.node_ids
                v1 = node_voltages.get(n1, 0)
                v2 = node_voltages.get(n2, 0)
                branch_currents[comp.label] = (v1 - v2) / comp.value

        return node_voltages, branch_currents
