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

class TestParseUseString(unittest.TestCase):

    def setUp(self):
        self.env = Environment(rootdir='/')

    def test_basic(self):
        lt, p = self.env._parse_use_string('hi')
        self.assertEquals(lt, 'hi')
        self.assertIsNone(p)

    def test_from(self):
        lt, p = self.env._parse_use_string('hi from foo.bar')
        self.assertEquals(lt, 'hi')
        self.assertEquals(p, 'foo.bar')

    def test_bad(self):
        with self.assertRaises(ValueError):
            self.env._parse_use_string('hi form fb')
