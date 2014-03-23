"""
Tests some basic stuff
"""
import unittest

from loader_manager import LoaderManager

class TestLoader(object):
    tag = 'ok'

class TestGetLoader(unittest.TestCase):

    def runTest(self):
        lm = LoaderManager()
        o = TestLoader()
        lm.register(o)
        self.assertIs(o, lm.get_loader('ok'))

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
