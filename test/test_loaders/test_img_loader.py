"""
tests for the img loader
"""
import unittest
import tempfile
import re
import base64

from bs4 import BeautifulSoup

from makejank.environment import Environment
from makejank.loaders import ImgLoader

import test.helpers

env = Environment(rootdir='/')

TEST_IMG = test.helpers.test_datafile('example/blue_arrow.png')

class TestLoad(unittest.TestCase):

    def runTest(self):
        loader = ImgLoader()
        result = loader.load(env, TEST_IMG, {})

        result_soup = BeautifulSoup(result)
        child_nodes = list(result_soup.children)
        self.assertEqual(len(child_nodes), 1, "Result should have one node")

        img_tag = child_nodes[0]
        self.assertEqual(img_tag.name, 'img', "Result should be a img tag")

        src = img_tag['src']

        # its a base64 encoded data uri
        _, mimetype, _, data = re.split(r'[:;,]', src)
        pure_data = re.sub(r'\s', '', data)

        self.assertEqual(mimetype, 'image/png')

        res_image = base64.b64decode(pure_data)
        with open(TEST_IMG, 'rb') as i:
            source_image = i.read()
        self.assertEqual(res_image, source_image)
