import unittest
import time
import tempfile
import shutil

from makejank.caches import MemoryCache, FilesystemCache, TestingCache

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

    def test_flush(self):
        """
        After flush, errthing should be gone.
        """
        cache = self.get_cache()
        cache.put('k', 'v')
        cache.put('k2', '567')
        cache.flush()
        self.assertIsNone(cache.get('k'))
        self.assertIsNone(cache.get('k2'))
        self.assertIsNone(cache.last_modified('k'))
        self.assertIsNone(cache.last_modified('k2'))

    def _type_check(self, v):
        """
        Can handle lots of types.
        - tuples
        - lists
        - numbers
        - dicts with string keys
        - <containing eachother>

        - Cache does NOT check this... TODO?
        """
        cache = self.get_cache()
        cache.put('k', v)
        r = cache.get('k')
        self.assertEquals(r, v)

    def test_int(self):
        self._type_check(9)

    def test_float(self):
        self._type_check(18.192)

    def test_tuple(self):
        self._type_check(('a', 'b'))

    def test_list(self):
        self._type_check(['a', 'b'])

    def test_dict(self):
        self._type_check({'a':1, 'b':2})

    def test_complex_obj(self):
        o = (
            ['a', 9],
            {
                'b': (1, 'b'),
                'fb': [1, 8.18, 'n', (6, (2.0,)), {'n':9}],
            },
        )
        self._type_check(o)

    def test_set(self):
        self._type_check(set([1,2,3,'a','b','c']))

    def test_change_to_string(self):
        self._type_check(5)
        self._type_check('hello')

    def test_change_from_string(self):
        self._type_check('hello')
        self._type_check(5)

class TestMemoryCache(CacheMixin, unittest.TestCase):

    get_cache = lambda s : MemoryCache()

class TestFilesystemCache(CacheMixin, unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def get_cache(self):
        return FilesystemCache(self.tempdir)

    def tearDown(self):
        shutil.rmtree(self.tempdir)
