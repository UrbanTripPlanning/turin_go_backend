import logging
import datetime
import httpx
import pandas as pd
import networkx as nx
import geopandas as gpd
from datetime import datetime
from typing import Optional, List

import torch
from shapely.geometry import shape
from utils.load import DATA_SERVICE_URL
from utils.times import timestamp2datetime
from networkx.readwrite import json_graph
from traffic_service.services.nn.inference import EdgeWeightPredictor


class RoadDataProcessor:
    def __init__(self):
        """
        Initialize the RoadDataProcessor instance.
        Sets up variables for road, traffic, and weather data, as well as the final GeoDataFrame.
        """
        self.road_data: Optional[List[dict]] = None
        self.traffic_data: Optional[List[dict]] = None
        self.weather_data: Optional[pd.DataFrame] = None
        self.geo_df: Optional[gpd.GeoDataFrame] = None
        logging.info("RoadDataProcessor instance created.")

    async def load_all_data(self, timestamp=None) -> None:
        """
        Load data asynchronously from the 'road', 'weather', and 'traffic' collections.
        """
        logging.info("Starting to load all data (road, traffic, weather).")
        self.road_data = await self._query_road_data()
        logging.info(f"Loaded {len(self.road_data)} road documents.")
        self.weather_data = await self.process_weather_data(timestamp)
        logging.info(f"Loaded weather data.")
        self.traffic_data = await self._query_traffic_data(timestamp)
        logging.info(f"Loaded {len(self.traffic_data)} traffic documents.")

    @staticmethod
    async def _query_road_data():
        """
        Query road data from the designated ROAD_COLLECTION.
        """
        logging.info("Querying road data...")
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f'{DATA_SERVICE_URL}/road/info')
        documents = resp.json()
        logging.info(f"Queried road data: {len(documents)} documents found.")
        return documents

    @staticmethod
    async def _query_traffic_data(timestamp=None):
        """
        Query traffic data using an aggregation pipeline based on a specific hour.
        The hour is determined from timestamp, or the current time.
        """
        logging.info("Querying traffic data...")
        if timestamp is None:
            timestamp = int(datetime.now().timestamp())
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f'{DATA_SERVICE_URL}/traffic/road/info', params={'timestamp': timestamp})
        documents = resp.json()
        logging.info(f"Queried traffic data: {len(documents)} documents found.")
        return documents

    @staticmethod
    async def process_weather_data(timestamp=None) -> pd.DataFrame:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f'{DATA_SERVICE_URL}/weather/info')
        documents = resp.json()
        logging.info(f"Queried weather data: {len(documents)} documents found.")

        df = pd.DataFrame(documents)
        df.set_index('datetime', inplace=True)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        if timestamp is not None:
            time = timestamp2datetime(timestamp)
        else:
            time = datetime.now()
        pos = df.index.get_indexer([time], method='nearest')[0]
        closest_row = df.iloc[pos]

        return closest_row

    @staticmethod
    def process_road_data(documents: List[dict]) -> gpd.GeoDataFrame:
        """
        Process road collection documents into a GeoDataFrame.
        Converts GeoJSON geometry to shapely objects.
        """
        if not documents:
            logging.warning("No road documents to process.")
            return gpd.GeoDataFrame()
        df = pd.DataFrame(documents)
        logging.info("Converting road geometry from GeoJSON to shapely objects.")
        df['geometry'] = df['geometry'].apply(lambda geom: shape(geom))
        geo_df = gpd.GeoDataFrame(df, geometry='geometry')
        logging.info("Processed road data into a GeoDataFrame.")
        return geo_df

    @staticmethod
    def process_traffic_data(documents: List[dict]) -> gpd.GeoDataFrame:
        """
        Process traffic collection documents into a GeoDataFrame.
        Renames the '_id' column to 'road_id' for merging purposes.
        """
        if not documents:
            logging.warning("No traffic documents to process.")
            return gpd.GeoDataFrame()
        traffic_df = pd.DataFrame(documents)
        logging.info("Renaming '_id' column to 'road_id' in traffic data.")
        traffic_df.rename(columns={"_id": "road_id"}, inplace=True)
        return traffic_df

    def build_network_geodataframe(self) -> Optional[gpd.GeoDataFrame]:
        """
        Convert raw traffic documents into a GeoDataFrame:
          - Parses each 'geometry' dict into a Shapely geometry.
          - Ensures the same schema when empty.
          - Assigns a defined CRS for spatial operations.
        """
        road_gdf = self.process_road_data(self.road_data)
        traffic_df = self.process_traffic_data(self.traffic_data)
        weather_df = self.weather_data

        if 'road_id' in road_gdf.columns:
            if not traffic_df.empty and 'road_id' in traffic_df.columns:
                road_gdf = road_gdf.merge(traffic_df, on="road_id", how="left", suffixes=("", "_traffic"))
                logging.info("Merged traffic data with road GeoDataFrame.")
            else:
                logging.info("Traffic data is empty or missing 'road_id'; skipping merge.")
        else:
            logging.warning("Common key 'road_id' not found in road data; merge skipped.")

        if not weather_df.empty:
            road_gdf['is_rain'] = weather_df['rain']
            road_gdf['weather_condition'] = weather_df['weather_condition']
        else:
            logging.warning("Empy weather data; skipping merge.")

        return road_gdf


class RoadNetwork:
    """
    Manages a directed road network:
      - Loads traffic data via RoadDataProcessor.
      - Optionally applies a GNN to predict or adjust edge weights.
      - Builds a NetworkX DiGraph with road segments and travel attributes.
    """
    def __init__(self, gnn_model: str = '') -> None:
        """
        Initialize the RoadNetwork instance.
        :param gnn_model: Model type ("GCN", "LSTM", or empty string to disable).
        """
        self.gnn_model = gnn_model
        self.gdf: Optional[gpd.GeoDataFrame] = None
        self.graph: Optional[nx.DiGraph] = None
        self.processor = RoadDataProcessor()
        self.predictor: Optional[EdgeWeightPredictor] = None

        print(f"[RoadNetwork] Initializing with model = {gnn_model}")
        if self.gnn_model:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.predictor = EdgeWeightPredictor(model_name="edge_autoencoder.pt", device=self.device)
            logging.info(f"{self.gnn_model} model and scalers loaded.")

        logging.info("RoadNetwork instance created. Processor initialized.")

    def to_dict(self):
        return json_graph.node_link_data(self.graph, edges="links")

    async def async_init(
            self,
            timestamp: int = None
    ) -> None:
        """
        Asynchronously initialize the network:
          1. Load traffic data via RoadDataProcessor.
          2. Build the underlying directed graph.
        """
        logging.info("Starting asynchronous initialization of RoadNetwork.")

        # Query and load data from all collections (only road data is available).
        await self.processor.load_all_data(timestamp)
        logging.info("Road data loaded from database.")

        # Process and merge the data into one GeoDataFrame (only road data used).
        self.gdf = self.processor.build_network_geodataframe()
        if self.gdf is not None:
            logging.info(f"GeoDataFrame built with {len(self.gdf)} records.")
        else:
            logging.warning("GeoDataFrame is empty after processing.")

        # Build the graph from the GeoDataFrame.
        self.build_graph()
        logging.info("RoadNetwork asynchronous initialization complete.")

    def build_graph(self) -> None:
        """
        Construct a directed NetworkX graph from the GeoDataFrame.
        Each DB record yields a one-way edge tail→head with its own attributes.
        """
        self.graph = nx.DiGraph()
        try:
            for index, row in self.gdf.iterrows():
                geom = row.geometry
                # Process only LineString geometries.
                if geom.geom_type != 'LineString':
                    continue

                # Extract tail/head IDs and their coordinates
                tail_id = int(row["tail"])
                head_id = int(row["head"])
                lon_tail, lat_tail = geom.coords[0]
                lon_head, lat_head = geom.coords[-1]
                road_id = int(row["road_id"])

                # Add each node once, storing its spatial position
                if tail_id not in self.graph:
                    self.graph.add_node(tail_id, pos=(lon_tail, lat_tail))
                if head_id not in self.graph:
                    self.graph.add_node(head_id, pos=(lon_head, lat_head))

                # Use provided 'length' if available; otherwise, compute from geometry.
                length = row.get('length', geom.length)
                # Calculate car travel time if average speed is provided.
                is_rain = row.get('is_rain', 0) == 1
                car_avg_speed = row.get('avg_speed_rain' if is_rain else 'avg_speed_clear', 0)
                car_travel_time = length / (car_avg_speed / 3.6) if car_avg_speed != 0 else 0
                self.graph.add_edge(
                    tail_id,
                    head_id,
                    road_id=road_id,
                    speed=car_avg_speed,
                    length=length,
                    time=car_travel_time,
                )

            # If using GNN-based weight prediction, overwrite or augment edge weights
            if self.gnn_model and self.predictor:
                weights = self.predictor.infer_edge_weights(self.graph)
                self.predictor.assign_weights_to_graph(self.graph, weights)

            logging.info(
                f"Graph built with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")
        except Exception as e:
            logging.error(f"Error building graph: {e}")
            raise
