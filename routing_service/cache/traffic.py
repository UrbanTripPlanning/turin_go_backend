import datetime
import asyncio
import httpx
import logging
from utils.load import TRAFFIC_SERVICE_URL


cache = {
    'data': None,
    'expired_at': 0
}


def get_traffic_data():
    curr = int(datetime.datetime.now().timestamp())
    if curr + 60 > cache['expired_at']:
        asyncio.create_task(load_traffic_data())
    return cache['data']


async def load_traffic_data():
    logging.info("load new traffic data...")
    curr = int(datetime.datetime.now().timestamp())
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{TRAFFIC_SERVICE_URL}/road/network', params={'timestamp': 1})
    data = resp.json()
    cache['data'] = data
    cache['expired_at'] = curr + 10*60


