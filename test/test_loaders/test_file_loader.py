"""
tests for the file loader
"""
import unittest
import tempfile

from makejank.environment import Environment
from makejank.loaders import FileLoader

import test.helpers

env = Environment(rootdir='/')

class TestDeps(unittest.TestCase):
    def runTest(self):
        loader = FileLoader()
        self.assertEqual(loader.dependencies(env, 'foo', {}), set([
            env.resolve_path('foo')
        ]))


class TestOK(unittest.TestCase):

    CONTENTS = 'FOOOO'

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()
        self.tempfile.write(self.CONTENTS)
        self.tempfile.flush()

    def runTest(self):
        loader = FileLoader()
        filename = self.tempfile.name
        result = loader.load(env, filename, {})
        self.assertEquals(result, self.CONTENTS)


class TestCannotFindFile(unittest.TestCase) :

    def runTest(self):
        loader = FileLoader()
        filename = test.helpers.nonexistent_filename()

        with self.assertRaises(ValueError) as e:
            loader.load(env, filename, {})
