"""
Basic tests for base loader
"""
import unittest

from makejank.loaders.base_loader import BaseLoader

class ProductionEnv(object):
    production = True

class Env(object):
    production = False

class TestSubLoader(BaseLoader):
    tag = 'test'


class TestSubLoaderNoCache(BaseLoader):
    tag = 'test'
    CACHE_RESULT = False


class TestProduct(unittest.TestCase):
    def test_not_production(self):
        l = TestSubLoader()
        expected = "test:foo:{'a':True}"
        self.assertEquals(l.product(Env, 'foo', {'a': True}), expected)

    def test_production(self):
        l = TestSubLoader()
        expected = "test:foo:{'a':True}:p"
        self.assertEquals(l.product(ProductionEnv, 'foo', {'a': True}), expected)


class TestProductNoCache(unittest.TestCase):
    def runTest(self):
        l = TestSubLoaderNoCache()
        self.assertIsNone(l.product(None, 'foo', {'a': True}))
