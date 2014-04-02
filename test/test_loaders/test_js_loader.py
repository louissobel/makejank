"""
tests for the js loader
"""
import unittest
import tempfile

from bs4 import BeautifulSoup

from makejank.environment import Environment
from makejank.loaders import JSLoader

import test.helpers

env = Environment(rootdir='/')

class TestDeps(unittest.TestCase):
    def runTest(self):
        loader = JSLoader()
        self.assertEqual(loader.dependencies(env, 'foo', {}), set([
            env.resolve_path('foo')
        ]))


class TestProduct(unittest.TestCase):
    def runTest(self):
        loader = JSLoader()
        self.assertIsNone(loader.product(env, 'foo', {}))


class TestOK(unittest.TestCase):

    SCRIPT = 'a'

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()
        self.tempfile.write(self.SCRIPT)
        self.tempfile.flush()

    def runTest(self):
        loader = JSLoader()
        filename = self.tempfile.name
        result = loader.load(env, filename, {})

        result_soup = BeautifulSoup(result)
        child_nodes = list(result_soup.children)
        self.assertEqual(len(child_nodes), 1, "Result should have one node")

        script_tag = child_nodes[0]
        self.assertEqual(script_tag.name, 'script', "Result should be a script tag")

        self.assertEqual(script_tag['type'], 'text/javascript', "Result should proper type")
        self.assertEqual(script_tag.text.strip(), self.SCRIPT)

class TestCannotFindFile(unittest.TestCase) :

    def runTest(self):
        loader = JSLoader()
        filename = test.helpers.nonexistent_filename()

        with self.assertRaises(ValueError) as e:
            loader.load(env, filename, {})
