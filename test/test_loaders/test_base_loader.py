"""
Basic tests for base loader
"""
import unittest

from makejank.loaders.base_loader import BaseLoader


class TestSubLoader(BaseLoader):
    tag = 'test'


class TestSubLoaderNoCache(BaseLoader):
    tag = 'test'
    CACHE_RESULT = False


class TestProduct(unittest.TestCase):
    def runTest(self):
        l = TestSubLoader()
        expected = "test:foo:{'a':True}"
        self.assertEquals(l.product(None, 'foo', {'a': True}), expected)


class TestProductNoCache(unittest.TestCase):
    def runTest(self):
        l = TestSubLoaderNoCache()
        self.assertIsNone(l.product(None, 'foo', {'a': True}))
