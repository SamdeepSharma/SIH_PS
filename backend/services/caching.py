from extensions import redis_client

def cache_set(key, value, timeout=300):
    redis_client.setex(key, timeout, value)

def cache_get(key):
    return redis_client.get(key)