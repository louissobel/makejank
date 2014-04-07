"""
sort of integration test here
"""
import unittest
import tempfile
import shutil

from makejank.loaders import *
from makejank.environment import Environment

import test.helpers

env = Environment(
    rootdir=test.helpers.datadir(),
    loaders = [
        YamlLoader(),
        CSSLoader(),
        JSLoader(),
        ImgLoader(),
        MakejankLoader(),
    ]
)

class TestDeps(unittest.TestCase):
    def runTest(self):
        # Heavily dependent on contents of page.
        loader = MakejankLoader()
        deps = loader.dependencies(env, 'example/page.html', {})
        self.assertEquals(deps, set(map(test.helpers.test_datafile, [
            'example/smiley.jpg',
            'example/base.html',
            'example/macros.html',
            'example/footer.html',
            'example/blue_arrow.png',
            'example/script.js',
            'example/style.css',
            'example/data.yml',
            'example/page.html',
        ])))

class TestRender(unittest.TestCase):
    def runTest(self):
        # For now, just test that it doesn't throw an error,
        # :/ jank.
        loader = MakejankLoader()
        rendered = loader.load(env, 'example/page.html', {})
