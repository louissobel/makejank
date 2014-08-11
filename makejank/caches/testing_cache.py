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

        # Use our own clock so the wall doesn't matter.
        self._clock = 0
        self._last_modified = {}

    def get(self, key):
        self.last_get = key
        return self.c.get(key)

    def put(self, key, value):
        self.last_put = (key, value)
        self._last_modified[key] = self._clock
        self._clock += 1
        return self.c.put(key, value)

    def last_modified(self, key):
        self.last_last_modified = key
        return self._last_modified.get(key)

    def flush(self):
        self.c.flush()