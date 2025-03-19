import asyncio
import time

import httpx
from utils.load import DATA_SERVICE_URL


async def traffic_data(timestamp: int):
    traffic_list = await get_traffic(timestamp)
    nodes = await get_position()
    node_geo = {}
    for node in nodes:
        node_geo[node['node_id']] = node['coordinates']
    results = []
    for traffic in traffic_list:
        results.append({
            'start': node_geo[traffic['tail']],
            'end': node_geo[traffic['head']],
            'flow_rate': traffic['speed']/50
        })
    return results


async def get_traffic(timestamp: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/traffic/info', params={'timestamp': timestamp})
    return resp.json()


async def get_position():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/position/info')
    return resp.json()
