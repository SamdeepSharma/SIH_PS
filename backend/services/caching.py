"""Caching utilities for the application."""
import pickle
import logging
from extensions import redis_client


def cache_set(key, value, timeout=300):
    """
    Set a value in the Redis cache.
    :param key: Cache key.
    :param value: Value to be cached.
    :param timeout: Cache expiration time in seconds (default is 300 seconds).
    :return: None
    """
    try:
        serialized_value = pickle.dumps(value)
        redis_client.setex(key, timeout, serialized_value)
        logging.debug("Value cached under key: %s", key)
    except Exception as err:
        logging.error("Failed to set cache for key %s: %s", key, str(err))

def cache_get(key):
    """
    Get a value from the Redis cache.
    :param key: Cache key.
    :return: Cached value or None if the key does not exist.
    """
    try:
        cached_value = redis_client.get(key)
        if cached_value is not None:
            deserialized_value = pickle.loads(cached_value)
            logging.debug("Cache hit for key: %s", key)
            return deserialized_value
        logging.debug("Cache miss for key: %s", key)
        return None
    except Exception as e:
        logging.error("Failed to get cache for key %s: %s", key, str(e))
        return None

def cache_delete(key):
    """
    Delete a key from the Redis cache.
    :param key: Cache key.
    :return: None
    """
    try:
        redis_client.delete(key)
        logging.debug("Cache key deleted: %s", key)
    except Exception as err:
        logging.error("Failed to delete cache for key %s: %s", key, str(err))
