"""
cache for testing that wraps a MemoryCache
"""
from .memory_cache import MemoryCache

class TestingCache(object):

    def __init__(self):
        self.c = MemoryCache()
        self.last_get = None
        self.last_put = None
        self.last_last_modified = None

    def get(self, key):
        self.last_get = key
        return self.c.get(key)

    def put(self, key, value):
        self.last_put = (key, value)
        return self.c.put(key, value)

    def last_modified(self, key):
        self.last_last_modified = key
        return self.c.last_modified(key)
    