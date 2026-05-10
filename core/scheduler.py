from core.node_client import NodeClient


class Scheduler:

    def __init__(self, nodes: list[NodeClient]):
        self.nodes = nodes

    def pick_node(self) -> NodeClient:
        if not self.nodes:
            raise Exception("No nodes available")
        return self.nodes[0]