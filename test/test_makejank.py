"""
sort of integration test here
"""
import unittest

import environment
from loaders import *
from caches import FilesystemCache

import test.helpers

env = environment.Environment(
    rootdir=test.helpers.datadir(),
    loaders=[
        YamlLoader(),
        CSSLoader(),
        JSLoader(),
        ImgLoader(),
    ],
    cache=FilesystemCache('.makejank_cache')
)

class TestDeps(unittest.TestCase):
    def runTest(self):
        # Heavily dependent on contents of page.
        deps = env.get_deps('example/page.html')
        self.assertEquals(deps, set([
            test.helpers.test_datafile('example/smiley.jpg')
        ]))

class TestRender(unittest.TestCase):
    def runTest(self):
        # For now, just test that it doesn't throw an error,
        # :/ jank.
        rendered = env.render('example/page.html')
