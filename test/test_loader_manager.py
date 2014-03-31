"""
Tests some basic stuff
"""
import unittest

from makejank.loader_manager import LoaderManager
from makejank.caches import TestingCache, NoopCache

import test.helpers

class TestLoader(object):
    tag = 'test'

    LOAD_RESULT = "test product contents"
    PRODUCT_NAME = "test_product"

    def product(self, env, args):
        return self.PRODUCT_NAME

    def dependencies(self, env, args):
        # No Deps
        return set()

    def load(self, env, args):
        return self.LOAD_RESULT

class TestLoaderWithNonexistentDependency(TestLoader):
    def dependencies(self, env, args):
        return set(['/' + test.helpers.nonexistent_filename()])

class TestLoaderNoCache(TestLoader):
    def product(self, env, args):
        return None

class TestGetLoader(unittest.TestCase):

    def runTest(self):
        lm = LoaderManager()
        o = TestLoader()
        lm.register(o)
        self.assertIs(o, lm.get_loader('test'))

class TestLoaderNotThere(unittest.TestCase):

    def runTest(self):
        lm = LoaderManager()
        with self.assertRaises(KeyError):
            lm.get_loader('not_there')

class TestCheckLoadResultType(unittest.TestCase):

    def setUp(self):
        lm = LoaderManager()
        self.c = lm.check_load_result_type

    def test_allow_string(self):
        ok, err = self.c("Hi")
        self.assertTrue(ok)

    def test_allow_unicode(self):
        ok, err = self.c(u'foo')
        self.assertTrue(ok)

    def test_allow_tuple(self):
        ok, err = self.c(('booop', {'a':5}))
        self.assertTrue(ok)

    def test_allow_unicode_tuple(self):
        ok, err = self.c((u'har', 9009))
        self.assertTrue(ok)

    def test_fail_wrong_type(self):
        ok, err = self.c(9)
        self.assertFalse(ok)

    def test_fail_long_tuple(self):
        ok, err = self.c(('a', 1, 2))
        self.assertFalse(ok)

    def test_fail_short_tuple(self):
        ok, err = self.c(('a',))
        self.assertFalse(ok)

    def test_fail_bad_tuple_first(self):
        ok, err = self.c((9, 9))
        self.assertFalse(ok)

    def test_fail_bad_tuple_second(self):
        ok, err = self.c(('a', object))
        self.assertFalse(ok)

class TestCheckDepsTypes(unittest.TestCase):

    def setUp(self):
        lm = LoaderManager()
        self.c = lm.check_deps_types

    def test_ok(self):
        ok, err = self.c(set(['/a', '/b/c/d.f']))
        self.assertTrue(ok)

    def test_bad(self):
        ok, err = self.c(set(['/a', 'b/c/d']))
        self.assertFalse(ok)

    def test_not_a_set(self):
        ok, err = self.c(8)
        self.assertFalse(ok)

#########
# Tests for service

class TestService(unittest.TestCase):
    """
    Checks that service calls load
    """
    def runTest(self):
        cache = TestingCache()
        lm = LoaderManager(cache)
        lm.register(TestLoader())
        self.assertEqual(lm.service(None, 'test', None), TestLoader.LOAD_RESULT)


class TestServiceWithoutCache(unittest.TestCase):
    """
    survive without a cache
    """
    def runTest(self):
        lm = LoaderManager()
        lm.register(TestLoader())
        self.assertEqual(lm.service(None, 'test', None), TestLoader.LOAD_RESULT)


class TestServicePullsFromCache(unittest.TestCase):
    """
    TestLoader is never stale (no deps) so should get result from cache if its there
    """
    def runTest(self):
        cache = TestingCache()
        lm = LoaderManager(cache)
        lm.register(TestLoader())
        cache.put(TestLoader.PRODUCT_NAME, "tricked you")
        self.assertEqual(lm.service(None, 'test', None), "tricked you")
        self.assertEqual(cache.last_get, TestLoader.PRODUCT_NAME)


class TestServiceCacheStale(unittest.TestCase):
    """
    TestLoaderWithNonexistentDependency is always stale, 
    so needs to compute result then put in the value
    """
    def runTest(self):
        cache = TestingCache()
        lm = LoaderManager(cache)
        lm.register(TestLoaderWithNonexistentDependency())
        cache.put(TestLoader.PRODUCT_NAME, "tricked you")
        # Make sure it ignores the "tricked you" in the cache.
        self.assertEqual(lm.service(None, 'test', None), TestLoader.LOAD_RESULT)
        self.assertEqual(cache.last_put, (TestLoader.PRODUCT_NAME, TestLoader.LOAD_RESULT))

class TestServiceNoCache(unittest.TestCase):
    """
    dont ever cache!
    """
    def runTest(self):
        cache = TestingCache()
        lm = LoaderManager(cache)
        lm.register(TestLoaderNoCache())
        self.assertEqual(lm.service(None, 'test', None), TestLoader.LOAD_RESULT)
        self.assertEqual(cache.last_put, None)
        self.assertEqual(cache.last_get, None)

    