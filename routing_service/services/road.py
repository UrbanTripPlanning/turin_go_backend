import logging
import geopandas as gpd
from typing import Tuple, Optional
from networkx.readwrite import json_graph
from utils.distance import euclidean_distance


class RoadNetwork:
    """
    Class to manage a road network loaded from a MongoDB collection via the asynchronous Database module.

    Handles:
      - Asynchronous initialization of the database connection.
      - Creating a GeoDataFrame from road data.
      - Building a NetworkX graph from road geometries.
    """

    def __init__(self, graph_data) -> None:
        """
        Initialize the RoadNetwork instance.
        """
        self.gdf: Optional[gpd.GeoDataFrame] = None
        self.graph = json_graph.node_link_graph(graph_data, edges="links")
        logging.info("RoadNetwork instance created. Processor initialized.")

    def _find_nearest_node(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """
        Find the node in the graph closest to the given point using Euclidean distance.

        :param point: Tuple (x, y) representing the query point.
        :return: The nearest node (x, y) in the graph.
        """
        nearest: Optional[Tuple[float, float]] = None
        min_dist = float('inf')
        for node in self.graph.nodes():
            dist = euclidean_distance(node, point)
            if dist < min_dist:
                min_dist = dist
                nearest = node
        if nearest is None:
            logging.error("No node found in the graph for the given point.")
            raise ValueError("No node found in the graph.")
        logging.debug(f"Nearest node to {point} is {nearest} with distance {min_dist}")
        return nearest

    def ensure_node(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """
        Ensure that the point is a node in the graph. If not, return the nearest node.

        :param point: Tuple (x, y) representing the point.
        :return: A node (x, y) present in the graph.
        """
        if point not in self.graph.nodes():
            nearest = self._find_nearest_node(point)
            logging.info(f"Point {point} not found among nodes. Using nearest node: {nearest}")
            return nearest
        logging.debug(f"Point {point} exists in the graph.")
        return point
