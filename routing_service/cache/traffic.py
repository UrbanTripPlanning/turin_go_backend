import datetime
import asyncio
import time

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
    curr = int(datetime.datetime.now().timestamp())
    for _ in range(5):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(f'{TRAFFIC_SERVICE_URL}/road/network')
            resp.raise_for_status()
            data = resp.json()
            cache['data'] = data
            cache['expired_at'] = curr + 10*60
            return
        except httpx.HTTPStatusError as e:
            print(f'call traffic service api fail: error code: {e.response.status_code}')
        except httpx.ReadTimeout:
            print(f'traffic service api read timeout')
        except httpx.RequestError as e:
            print(f'call traffic service api request error: {str(e)}')
        except Exception as e:
            print(f'call traffic service api fail: {e}')
        time.sleep(5)
    raise RuntimeError("load traffic data fail")
