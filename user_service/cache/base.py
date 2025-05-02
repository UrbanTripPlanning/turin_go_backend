import datetime

cache = {}


def set_cache(key: str, value, expire_ts):
    cache[key] = (value, expire_ts)


def get_cache(key: str):
    now = int(datetime.datetime.now().timestamp())
    (value, expire_ts) = cache.get(key)
    if now > expire_ts:
        del cache[key]
        return None
    return value


def list_cache(prefix: str):
    now = int(datetime.datetime.now().timestamp())
    result = []
    for key, (value, expire_ts) in list(cache.items()):
        if key.startswith(prefix) is False:
            continue
        if now > expire_ts:
            del cache[key]
            continue
        result.append(value)
    return result


def delete_cache(key: str):
    del cache[key]
