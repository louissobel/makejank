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
