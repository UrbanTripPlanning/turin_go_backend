import datetime
import time
from routing_service.cache.traffic import traffic_graph_cache


async def load_current_traffic():
    await traffic_graph_cache.load_traffic_data()


async def load_future_traffic():
    now = int(datetime.datetime.now().timestamp())
    for offset in range(1, 7*24+1):
        time.sleep(5)
        ts = now + 60 * 60 * offset
        await traffic_graph_cache.load_traffic_data(ts)
