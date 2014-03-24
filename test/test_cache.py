import unittest
import time

from caches import MemoryCache

class CacheMixin(object):

    def test_put_key(self):
        #happypath
        cache = self.get_cache()
        cache.put('key', 'abc')
        r = cache.get('key')
        self.assertEquals(r, 'abc')

    def test_put_overwrite(self):
        cache = self.get_cache()
        cache.put('key', 'abc')
        cache.put('key', 'xyz')
        r = cache.get('key')
        self.assertEquals(r, 'xyz')

    def test_get_not_there(self):
        cache = self.get_cache()
        r = cache.get('key')
        self.assertIsNone(r)

    def test_last_modified(self):
        "Simple last modified"
        now = int(time.time())
        cache = self.get_cache()
        cache.put('key', 'abc')
        r = cache.last_modified('key')
        self.assertTrue(r >= now)

    def test_last_modified_updates(self):
        cache = self.get_cache()
        cache.put('key', 'old')
        time.sleep(1) # :/
        now = int(time.time())
        cache.put('key', 'new')
        r = cache.last_modified('key')
        self.assertTrue(r >= now)

    def test_last_modified_not_there(self):
        cache = self.get_cache()
        r = cache.last_modified('key')
        self.assertIsNone(r)

class TestMemoryCache(CacheMixin, unittest.TestCase):

    get_cache = lambda s : MemoryCache()
