"""
sort of integration test here
"""
import unittest
import tempfile
import shutil

from makejank import environment
from makejank.loaders import *
from makejank.caches import FilesystemCache

import test.helpers

def setup_module():
    global env
    global tempdir

    tempdir = tempfile.mkdtemp()
    env = environment.Environment(
        rootdir=test.helpers.datadir(),
        loaders=[
            YamlLoader(),
            CSSLoader(),
            JSLoader(),
            ImgLoader(),
        ],
        cache=FilesystemCache(tempdir)
    )

class TestDeps(unittest.TestCase):
    def runTest(self):
        # Heavily dependent on contents of page.
        deps = env.get_deps('example/page.html')
        self.assertEquals(deps, set(map(test.helpers.test_datafile, [
            'example/smiley.jpg',
            'example/base.html',
            'example/macros.html',
            'example/footer.html',
            'example/blue_arrow.png',
        ])))

class TestRender(unittest.TestCase):
    def runTest(self):
        # For now, just test that it doesn't throw an error,
        # :/ jank.
        rendered = env.render('example/page.html')

def teardown_module():
    global tempdir
    shutil.rmtree(tempdir)
