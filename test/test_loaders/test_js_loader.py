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


class TestProcessContents(unittest.TestCase):

    SCRIPT = 'a'

    def runTest(self):
        loader = JSLoader()
        result = loader.process_file_contents(self.SCRIPT)

        result_soup = BeautifulSoup(result)
        child_nodes = list(result_soup.children)
        self.assertEqual(len(child_nodes), 1, "Result should have one node")

        script_tag = child_nodes[0]
        self.assertEqual(script_tag.name, 'script', "Result should be a script tag")

        self.assertEqual(script_tag['type'], 'text/javascript', "Result should proper type")
        self.assertEqual(script_tag.text.strip(), self.SCRIPT)
