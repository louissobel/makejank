"""
tests for the css loader
"""
import unittest
import tempfile

from bs4 import BeautifulSoup

from makejank.environment import Environment
from makejank.loaders import CSSLoader

import test.helpers

env = Environment(rootdir='/')

class TestOK(unittest.TestCase):

    STYLE = 'a'

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()
        self.tempfile.write(self.STYLE)
        self.tempfile.flush()

    def runTest(self):
        loader = CSSLoader()
        args = [self.tempfile.name]
        result = loader.load(env, args)

        result_soup = BeautifulSoup(result)
        child_nodes = list(result_soup.children)
        self.assertEqual(len(child_nodes), 1, "Result should have one node")

        script_tag = child_nodes[0]
        self.assertEqual(script_tag.name, 'style', "Result should be a script tag")

        self.assertEqual(script_tag['type'], 'text/css', "Result should proper type")
        self.assertEqual(script_tag.text.strip(), self.STYLE)

class TestCannotFindFile(unittest.TestCase) :

    def runTest(self):
        loader = CSSLoader()
        filename = test.helpers.nonexistent_filename()

        args = [filename]
        with self.assertRaises(ValueError) as e:
            loader.load(env, args)
