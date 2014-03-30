import unittest

from makejank.environment import Environment

import test.helpers

class TestEnvironmentResolvePath(unittest.TestCase):

    def runTest(self):
        e = Environment(rootdir='/a/b')
        self.assertEquals('/a/b/c', e.resolve_path('c'))

class TestEnvironmentResolveAbsPath(unittest.TestCase):

    def runTest(self):
        e = Environment(rootdir='/a/b')
        self.assertEquals('/x/y/z', e.resolve_path('/x/y/z'))

class TestEnvironmentRequiresAbsoluteRootdir(unittest.TestCase):

    def runTest(self):
        with self.assertRaises(ValueError):
            Environment('a/b/c')

