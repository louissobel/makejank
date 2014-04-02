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


def parse_datauri(datauri):
    # its a base64 encoded data uri
    _, mimetype, _, data = re.split(r'[:;,]', datauri)
    pure_data = re.sub(r'\s', '', data)
    return mimetype, pure_data


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
        mimetype, data = parse_datauri(src)
        self.assertEqual(mimetype, 'image/png')

        res_image = base64.b64decode(data)
        with open(TEST_IMG, 'rb') as i:
            source_image = i.read()
        self.assertEqual(res_image, source_image)


class TestDefaultMimetype(unittest.TestCase):

    def runTest(self):
        t = tempfile.NamedTemporaryFile()
        loader = ImgLoader()
        result = loader.load(env, t.name, {})

        src = list(BeautifulSoup(result).children)[0]['src'] # :/
        mimetype, _ = parse_datauri(src)
        self.assertEqual(mimetype, 'application/octet-stream')
    