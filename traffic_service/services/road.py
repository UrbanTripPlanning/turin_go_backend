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

    async def load_all_data(self, start_time=None, end_time=None) -> None:
        """
        Load data asynchronously from the 'road', 'weather', and 'traffic' collections.
        """
        logging.info("Starting to load all data (road, traffic, weather).")
        self.road_data = await self._query_road_data()
        logging.info(f"Loaded {len(self.road_data)} road documents.")
        self.weather_data = await self.process_weather_data(start_time, end_time)
        logging.info(f"Loaded weather data.")
        self.traffic_data = await self._query_traffic_data(start_time, end_time)
        logging.info(f"Loaded {len(self.traffic_data)} traffic documents.")

    @staticmethod
    async def _query_road_data():
        """
        Query road data from the designated ROAD_COLLECTION.
        """
        logging.info("Querying road data...")
        async with httpx.AsyncClient() as client:
            resp = await client.get(f'{DATA_SERVICE_URL}/road/info')
        documents = resp.json()
        logging.info(f"Queried road data: {len(documents)} documents found.")
        return documents

    @staticmethod
    async def _query_traffic_data(start_time=None, end_time=None):
        """
        Query traffic data using an aggregation pipeline based on a specific hour.
        The hour is determined from start_time, end_time, or the current time.
        """
        logging.info("Querying traffic data...")
        if start_time is not None:
            timestamp = int(start_time.timestamp())
        elif end_time is not None:
            timestamp = int(end_time.timestamp())
        else:
            timestamp = int(datetime.now().timestamp())

        async with httpx.AsyncClient() as client:
            resp = await client.get(f'{DATA_SERVICE_URL}/traffic/road/info', params={'timestamp': timestamp})
        documents = resp.json()
        logging.info(f"Queried traffic data: {len(documents)} documents found.")
        return documents

    @staticmethod
    async def process_weather_data(start_time, end_time) -> pd.DataFrame:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f'{DATA_SERVICE_URL}/weather/info')
        documents = resp.json()
        logging.info(f"Queried weather data: {len(documents)} documents found.")

        df = pd.DataFrame(documents)
        df.set_index('datetime', inplace=True)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        if start_time is not None:
            time = start_time
        elif end_time is not None:
            time = end_time
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
        Process and merge road, traffic, and weather data into a single GeoDataFrame for the network.
        """
        logging.info("Building network GeoDataFrame from road and. traffic data, and weather data.")
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
    Class to manage a road network loaded from a MongoDB collection via the asynchronous Database module.

    Handles:
      - Asynchronous initialization of the database connection.
      - Creating a GeoDataFrame from road data.
      - Building a NetworkX graph from road geometries.
    """

    def __init__(self, gnn_model: str = '') -> None:
        """
        Initialize the RoadNetwork instance.
        :param gnn_model: Model type ("GCN", "STGCN", or empty string to disable).
        """
        self.gnn_model = gnn_model
        self.gdf: Optional[gpd.GeoDataFrame] = None
        self.graph: Optional[nx.Graph] = None
        self.processor = RoadDataProcessor()
        self.predictor: Optional[EdgeWeightPredictor] = None

        print(f"[RoadNetwork] Initializing with model = {gnn_model}")
        if self.gnn_model:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.predictor = EdgeWeightPredictor(model_name="edge_autoencoder.pt", device=self.device)
            logging.info(f"{self.gnn_model} model and scalers loaded.")

        logging.info("RoadNetwork instance created. Processor initialized.")
        print("[RoadNetwork] Model loaded.")

    def to_dict(self):
        return json_graph.node_link_data(self.graph, edges="links")

    async def async_init(
            self,
            start_time: datetime = None,
            end_time: datetime = None
    ):
        """
        Asynchronously initialize the database connection, load road data,
        and build the NetworkX graph.
        """
        logging.info("Starting asynchronous initialization of RoadNetwork.")

        # Query and load data from all collections (only road data is available).
        await self.processor.load_all_data(start_time, end_time)
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
        Build a NetworkX graph from the GeoDataFrame.
        Iterates through each road record and adds an edge using its geometry.
        """
        self.graph = nx.Graph()
        try:
            for index, row in self.gdf.iterrows():
                geom = row['geometry']
                # Process only LineString geometries.
                if geom.geom_type != 'LineString':
                    continue
                start = tuple(geom.coords[0])
                end = tuple(geom.coords[-1])
                # Use provided 'length' if available; otherwise, compute from geometry.
                length = row.get('length', geom.length)
                # Calculate car travel time if average speed is provided.
                is_rain = row.get('is_rain', 0) == 1
                car_avg_speed = row.get('avg_speed_rain' if is_rain else 'avg_speed_clear', 0)
                car_travel_time = length / (car_avg_speed / 3.6) if car_avg_speed != 0 else 0
                # Add weather information
                weather_condition = row.get('weather_condition', 'empty')
                self.graph.add_edge(
                    start,
                    end,
                    spped=car_avg_speed,
                    length=length,
                    time=car_travel_time,
                )
                logging.debug(
                    f"Edge added from {start} to {end}: length={length}, car_travel_time={car_travel_time}, "
                    f"weather_condition={weather_condition}")

            if self.gnn_model and self.predictor:
                weights = self.predictor.infer_edge_weights(self.graph)
                self.predictor.assign_weights_to_graph(self.graph, weights)

            logging.info(
                f"Graph built with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")
        except Exception as e:
            logging.error(f"Error building graph: {e}")
            raise
