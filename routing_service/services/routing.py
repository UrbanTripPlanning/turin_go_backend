import time
import logging
import networkx as nx
from enum import Enum
from datetime import datetime
from utils.distance import euclidean_distance
from typing import Tuple, Optional, List
from routing_service.services.road import RoadNetwork
from routing_service.models.api_route import SearchRouteRequest
from routing_service.cache.traffic import traffic_graph_cache


class TransportMode(Enum):
    FOOT = ('Foot', 72)         # 4.32 km/h -> m/min
    BIKE = ('Bike', 250)        # 15 km/h -> m/min
    CAR = ('Car', None)         # Use edge 'time' or 'weight'

    def __init__(self, mode_name: str, default_speed: Optional[float]):
        self.mode_name = mode_name
        self.default_speed = default_speed

    def __str__(self):
        return self.mode_name


class RoutePlanner:
    def __init__(
            self,
            network: RoadNetwork,
            transport_mode: TransportMode = TransportMode.FOOT,
            algorithm: str = 'A*',
            use_gnn: bool = False
    ) -> None:
        """
        :param network: Initialized RoadNetwork (with DiGraph and 'pos' on each node).
        :param transport_mode: One of TransportMode.
        :param algorithm: 'A*' or 'Dijkstra'.
        :param use_gnn: If True and mode == CAR, use edge['weight'] instead of ['time'].
        """
        self.network = network
        self.graph: nx.DiGraph = network.graph
        self.transport_mode = transport_mode
        self.algorithm = algorithm
        self.use_gnn = use_gnn
        logging.info(
            f"Initialized RoutePlanner with transport_mode: {self.transport_mode.mode_name}, algorithm: {self.algorithm}")

    def _select_cost_attribute(self) -> str:
        """
        Return the edge attribute used for path cost:
          - FOOT/BIKE → 'length'
          - CAR → 'weight' if use_gnn else 'time'.
        """
        if self.transport_mode == TransportMode.CAR:
            return "weight" if self.use_gnn else "time"
        return "length"

    def _run_path_algorithm(
        self,
        G: nx.Graph,
        source: int,
        target: int,
        cost_attr: str
    ) -> List[int]:
        """
        Execute the chosen pathfinding algorithm on graph G
        and return a list of node IDs.
        """
        if self.algorithm.lower() == "dijkstra":
            return nx.dijkstra_path(G, source, target, weight=cost_attr)

        # A* with Euclidean heuristic on node positions
        def heuristic(x: int, y: int) -> float:
            pu = tuple(G.nodes[x]["pos"])
            pv = tuple(G.nodes[y]["pos"])
            return euclidean_distance(pu, pv)

        return nx.astar_path(
            G, source, target,
            heuristic=heuristic,
            weight=cost_attr
        )

    def compute(
            self,
            source_point: Tuple[float, float],
            target_point: Tuple[float, float]
    ) -> Tuple[Optional[List[Tuple[float, float]]], float, int, Optional[float]]:
        """
        Compute the optimal route from source to target.
        CAR: directed; FOOT/BIKE: undirected.
        Returns (list of (lon,lat), stats) or (None, None).
        """
        if self.graph is None:
            raise RuntimeError("Road graph is not initialized.")

        cost_attr = self._select_cost_attribute()
        source_id = self.network.match_node_id(source_point)
        target_id = self.network.match_node_id(target_point)

        if self.transport_mode == TransportMode.CAR:
            G = self.graph
        else:
            G = self.graph.to_undirected()

        start_time_compute = time.perf_counter()

        # Compute the route using the selected algorithm.
        if self.algorithm.lower() == 'dijkstra':
            try:
                path = nx.dijkstra_path(G, source_id, target_id, weight=cost_attr)
            except nx.NetworkXNoPath:
                logging.error("No route found using Dijkstra.")
                return None, 0.0, 0, None
        else:
            # Use A* algorithm by default.
            def heuristic(x: int, y: int) -> float:
                pu = tuple(G.nodes[x]["pos"])
                pv = tuple(G.nodes[y]["pos"])
                return euclidean_distance(pu, pv)

            try:
                path = nx.astar_path(G, source_id, target_id, heuristic=heuristic, weight=cost_attr)
            except nx.NetworkXNoPath:
                logging.error("No route found using A*.")
                return None, 0.0, 0, None

        exec_time = time.perf_counter() - start_time_compute
        logging.info(f"Route computation time: {exec_time:.6f} seconds using {self.algorithm.capitalize()}")

        routes_distance = 0.0
        routes_time = 0.0
        for u, v in zip(path[:-1], path[1:]):
            edge = G.get_edge_data(u, v, {}) or {}
            seg_len = edge.get("length", 0.0)
            if self.transport_mode == TransportMode.CAR:
                convert_rate = 1 / 60  # m/s -> m/min
                seg_time = edge.get("time", 0.0)*convert_rate
            else:
                speed = self.transport_mode.default_speed or 1.0
                seg_time = seg_len / speed
            routes_distance += seg_len
            routes_time += seg_time

        coord_path = [G.nodes[n]["pos"] for n in path]
        return coord_path, routes_distance, round(routes_time), exec_time


async def history(req: SearchRouteRequest):
    algorithm = 'A*'
    if req.start_at > 0:
        ts = datetime.fromtimestamp(req.start_at)
    elif req.end_at > 0:
        ts = datetime.fromtimestamp(req.end_at)
    else:
        ts = None
    data = await traffic_graph_cache.get_traffic_data(ts)
    result = {}
    network = RoadNetwork(data)
    walking_planner = RoutePlanner(network, transport_mode=TransportMode.FOOT, algorithm=algorithm)
    walking_path, walking_distance, walking_times, _ = walking_planner.compute(req.src_loc, req.dst_loc)
    result['walking'] = {
        'routes': walking_path,
        'distances': walking_distance,
        'times': walking_times
    }
    driving_planner = RoutePlanner(network, transport_mode=TransportMode.CAR, algorithm=algorithm)
    driving_path, driving_distance, driving_times, _ = driving_planner.compute(req.src_loc, req.dst_loc)
    result['driving'] = {
        'routes': driving_path,
        'distances': driving_distance,
        'times': driving_times
    }
    cycling_planner = RoutePlanner(network, transport_mode=TransportMode.BIKE, algorithm=algorithm)
    cycling_path, cycling_distance, cycling_times, _ = cycling_planner.compute(req.src_loc, req.dst_loc)
    result['cycling'] = {
        'routes': cycling_path,
        'distances': cycling_distance,
        'times': cycling_times
    }
    return result

