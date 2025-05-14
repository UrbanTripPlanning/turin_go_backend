import datetime
import pandas as pd
import httpx
from utils.load import DATA_SERVICE_URL


async def history_info(timestamp: int):
    traffic_list = await get_traffic(timestamp)
    nodes = await get_position()
    weather_info = await get_weather(timestamp)
    is_rain = weather_info['rain'] == 1
    node_geo = {}
    for node in nodes:
        node_geo[node['node_id']] = node['coordinates']
    results = []
    for traffic in traffic_list:
        results.append({
            'start': node_geo[traffic['tail']],
            'end': node_geo[traffic['head']],
            'flow_rate': traffic['speed_rain' if is_rain else 'speed_clear']/50
        })
    return results


async def get_traffic(timestamp: int):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f'{DATA_SERVICE_URL}/traffic/info', params={'timestamp': timestamp})
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        print(f'call data service api fail: error code: {e.response.status_code}')
    except httpx.ReadTimeout:
        print(f'data service api read timeout')
    except httpx.RequestError as e:
        print(f'call data service api request error: {str(e)}')
    except Exception as e:
        print(f'call data service api fail: {e}')
    return []


async def get_position():
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/position/info')
    return resp.json()


async def get_weather(timestamp: int):
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/weather/info')
    df = pd.DataFrame(resp.json())
    df.set_index('datetime', inplace=True)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    dt = datetime.datetime.fromtimestamp(timestamp)
    pos = df.index.get_indexer([dt], method='nearest')[0]
    closest_row = df.iloc[pos]
    return closest_row


async def predict_info(timestamp: int):
    return []
