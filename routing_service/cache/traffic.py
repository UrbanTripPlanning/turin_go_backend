import datetime
import time

import httpx
from utils.load import TRAFFIC_SERVICE_URL
from utils.cache import RedisClient, LocalCache
from utils.times import getInfoFromTimestamp


class TrafficGraphCache:
    def __init__(self):
        self.local_cache = LocalCache()
        self.redis_cache = RedisClient()
        self.KEY_TRAFFIC_GRAPH = "traffic_graph"
        self.KEY_LOCK_PREFIX = "lock:traffic_graph"

        self.local_ttl = 5*60
        self.redis_ttl = 60*60
        self.lock_timeout = 60

    def _get_latest_key(self):
        return f"{self.KEY_TRAFFIC_GRAPH}:latest"

    def _build_ts_key(self, ts):
        _, month, _, weekday, hour, _ = getInfoFromTimestamp(ts)
        return f'{self.KEY_TRAFFIC_GRAPH}:{month}_{weekday}_{hour}'

    def _acquire_lock(self, key):
        lock_key = f"{self.KEY_LOCK_PREFIX}{key}"
        result = self.redis_cache.set(lock_key, "1", nx=True, ex=self.lock_timeout)
        return result

    def _release_lock(self, key):
        self.redis_cache.delete(f"{self.KEY_LOCK_PREFIX}{key}")

    async def get_traffic_data(self, ts: int = None):
        if ts is None:
            key = self._get_latest_key()
            cache = self.local_cache
            ex = 10 * 60  # 10 minutes
        else:
            key = self._build_ts_key(ts)
            cache = self.redis_cache
            ex = 70 * 60  # 70 minutes

        data = cache.get(key)
        if data:
            return data

        if self._acquire_lock(key):
            data = await self.load_traffic_data(ts)
            if data:
                cache.set(key, data, ex=ex)
            self._release_lock(key)
            return data
        else:
            for _ in range(10):
                time.sleep(3)
                data = cache.get(key)
                if data:
                    return data
        return None

    @staticmethod
    async def load_traffic_data(ts=None):
        if ts is None:
            ts = int(datetime.datetime.now().timestamp())

        for _ in range(5):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.get(f'{TRAFFIC_SERVICE_URL}/road/network', params={'timestamp': ts})
                resp.raise_for_status()
                return resp.json()
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


traffic_graph_cache = TrafficGraphCache()
