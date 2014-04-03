"""
sort of integration test here
"""
import unittest
import tempfile
import shutil

from makejank import Makejank

import test.helpers

def setup_module():
    global mj
    global tempdir

    tempdir = tempfile.mkdtemp()
    mj = Makejank(
        cache_dir=tempdir,
        base_dir=test.helpers.datadir(),
    )

class TestDeps(unittest.TestCase):
    def runTest(self):
        # Heavily dependent on contents of page.
        deps = mj.get_deps('makejank', 'example/page.html')
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
        rendered = mj.render('makejank', 'example/page.html')

def teardown_module():
    global tempdir
    shutil.rmtree(tempdir)
