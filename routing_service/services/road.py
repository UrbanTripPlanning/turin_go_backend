import logging
import geopandas as gpd
from typing import Tuple, Optional
from networkx.readwrite import json_graph
from utils.distance import euclidean_distance


class RoadNetwork:
    """
    Manages a directed road network:
      - Loads traffic data via RoadDataProcessor.
      - Optionally applies a GNN to predict or adjust edge weights.
      - Builds a NetworkX DiGraph with road segments and travel attributes.
    """
    def __init__(self, graph_data) -> None:
        """
        Initialize the RoadNetwork instance.
        """
        self.gdf: Optional[gpd.GeoDataFrame] = None
        self.graph = json_graph.node_link_graph(graph_data, edges="links")
        logging.info("RoadNetwork instance created. Processor initialized.")

    def _find_nearest_node(self, point: Tuple[float, float]) -> int:
        """
        Find the nearest graph node to a given point using Euclidean distance.

        :param point: Tuple (lon, lat) to search from.
        :return: The node ID closest to the point.
        """
        if self.graph is None or not self.graph.nodes:
            raise RuntimeError("Graph is empty. Cannot find nearest node.")

        nearest_node = None
        min_dist = float('inf')
        for node, data in self.graph.nodes(data=True):
            node_point = data.get('pos')
            if node_point is None:
                continue
            d = euclidean_distance(node_point, point)
            if d < min_dist:
                min_dist = d
                nearest = node
        if nearest_node is None:
            raise RuntimeError(
                f"No graph node has a valid 'pos' attribute; "
                f"cannot snap point {point!r} to graph."
            )
        return nearest_node

    def match_node_id(self, point: Tuple[float, float]) -> int:
        """
        Ensure a point corresponds to a graph node. If not, snap to the nearest.

        :param point: Tuple (lon, lat)
        :return: Valid node ID in the graph.
        """
        if self.graph is None:
            raise RuntimeError("Graph not initialized.")

        # If already exactly at a node position, return that node
        for node, data in self.graph.nodes(data=True):
            if data.get("pos") == point:
                return node

        # Otherwise, find and return the nearest node
        return self._find_nearest_node(point)
