import json, os, time

_mem: dict = {}
_redis = None


def _r():
    global _redis
    url = os.getenv("REDIS_URL")
    if url and _redis is None:
        import redis
        _redis = redis.from_url(url, decode_responses=True)
    return _redis


def get(key: str):
    r = _r()
    if r:
        v = r.get(key)
        return json.loads(v) if v else None
    hit = _mem.get(key)
    return hit[1] if hit and hit[0] > time.time() else None


def set(key: str, value: dict, ttl: int = 300):
    r = _r()
    if r:
        r.setex(key, ttl, json.dumps(value))
    else:
        _mem[key] = (time.time() + ttl, value)
