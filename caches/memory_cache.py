"""
Cache interface

 - get(key)
 - last_modified(key) --> None (if not exists) or last modified in unix
 - put (key, value)
"""
import time

class MemoryCache(object):

    def __init__(self):
        self.inner = {}

    def last_modified(self, key):
        v = self.inner.get(key)
        if v is None:
            return None
        else:
            return v[1]

    def get(self, key):
        v = self.inner.get(key)
        if v is None:
            return None
        else:
            return v[0]

    def put(self, key, value):
        now = int(time.time())
        self.inner[key] = (value, now)


