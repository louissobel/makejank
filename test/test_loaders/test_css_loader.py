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

class TestProcessContents(unittest.TestCase):

    STYLE = 'a'

    def runTest(self):
        loader = CSSLoader()
        result = loader.process_file_contents(self.STYLE)

        result_soup = BeautifulSoup(result)
        child_nodes = list(result_soup.children)
        self.assertEqual(len(child_nodes), 1, "Result should have one node")

        script_tag = child_nodes[0]
        self.assertEqual(script_tag.name, 'style', "Result should be a script tag")

        self.assertEqual(script_tag['type'], 'text/css', "Result should proper type")
        self.assertEqual(script_tag.text.strip(), self.STYLE)
