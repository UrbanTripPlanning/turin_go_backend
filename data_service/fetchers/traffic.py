import pandas as pd
import geopandas as gpd
from dbfread import DBF
from shapely.geometry import mapping
from data_service.database import get_mongo_collection


def load_csv(file_path):
    return pd.read_csv(file_path)


def load_dbf(file_path):
    table = DBF(file_path, load=True)
    return pd.DataFrame(iter(table))


def add_node(data, node_id, coordinates):
    if node_id is None or node_id in data:
        return
    data[node_id] = {
        'node_id': node_id,
        'coordinates': coordinates
    }


def fetch_from_local():
    road_path = '../data/road_detail.dbf'
    road_df = load_dbf(road_path)
    road_data = road_df.rename(columns={'idno': 'road_id', 'leng': 'length'}).to_dict('records')
    pos_path = '../data/position/position.shp'
    pos_gpd = gpd.read_file(pos_path)
    pos_data = {}
    geo_data = {}
    for index, row in pos_gpd.iterrows():
        tail = row.get('tail')
        head = row.get('head')
        line = row.geometry
        coords = list(line.coords)
        if len(coords) < 2:
            continue
        tail_pos = coords[0]
        head_pos = coords[-1]
        add_node(pos_data, tail, list(tail_pos))
        add_node(pos_data, head, list(head_pos))
        geo_data[(tail, head)] = mapping(line)
    pos_collection = get_mongo_collection('position')
    _ = pos_collection.insert_many(list(pos_data.values()))

    for item in road_data:
        item['geometry'] = geo_data[(item['tail'], item['head'])]
    road_collection = get_mongo_collection('road')
    _ = road_collection.insert_many(road_data)




