import datetime
import redis
import json
from utils.load import REDIS_HOST


class LocalCache:
    def __init__(self):
        self.cache = {}

    def set(self, key, value, ex=None, ts=None):
        value = json.dumps(value)
        expire_time = None
        if ts:
            expire_time = ts
        if ex:
            expire_time = int(datetime.datetime.now().timestamp()) + ex
        self.cache[key] = (value, expire_time)

    def get(self, key):
        item = self.cache.get(key)
        if not item:
            return None
        value, expire_time = item

        now = int(datetime.datetime.now().timestamp())
        if expire_time and now > expire_time:
            del self.cache[key]
            return None
        return json.loads(value)

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]

    def list(self, prefix):
        result = []
        now = int(datetime.datetime.now().timestamp())
        for key, (value, expire_ts) in list(self.cache.items()):
            if key.startswith(prefix) is False:
                continue
            if now > expire_ts:
                del self.cache[key]
                continue
            result.append(json.loads(value))
        return result


class RedisClient:
    def __init__(self):
        self.cache = redis.Redis(
            host=REDIS_HOST,
            port=6379,
            decode_responses=True
        )

    def set(self, key, value, ex=None, ts=None, nx=None):
        value = json.dumps(value)
        now = int(datetime.datetime.now().timestamp())
        if ts and ts > now:
            ex = ts - now

        return self.cache.set(key, value, ex=ex, nx=nx)

    def get(self, key):
        value = self.cache.get(key)
        if value is None:
            return None
        return json.loads(value)

    def delete(self, key):
        self.cache.delete(key)

    def list(self, prefix):
        result = []
        for key in self.cache.scan_iter(f'{prefix}*'):
            value = self.cache.get(key)
            if value:
                result.append(json.loads(value))

        return result
