"""
Runs a makejank

Doesnt actually shell out, rather, fakes sys.argv and calls main.main
"""
import unittest
import os
import sys
import os.path
import tempfile
import shutil
import shlex
import StringIO

from bs4 import BeautifulSoup

from makejank import main

def capture_main_output():
    oldstdout = sys.stdout
    newstdout = StringIO.StringIO()
    sys.stdout = newstdout
    main.main()
    sys.stdout = oldstdout

    newstdout.seek(0)
    return newstdout.read()

class IntegrationTestMixin(object):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)


class TestJankfile(IntegrationTestMixin, unittest.TestCase):

    def runTest(self):
        command = "makejank -j example/Jankfile --output-dir %s" % self.tempdir
        # should use shlex...
        sys.argv = command.split(' ')

        main.main()

        # Check it
        if not os.path.exists(os.path.join(self.tempdir, 'index.html')):
            raise AssertionError('index.html not created')

        if not os.path.exists(os.path.join(self.tempdir, 'detail.html')):
            raise AssertionError('detail.html not created')


class TestSource(unittest.TestCase):

    def runTest(self):
        command = "makejank example/index.html -b example/"
        sys.argv = command.split(' ')

        result = capture_main_output()

        # Do a basic test.
        soup = BeautifulSoup(result)
        titletag = soup.find('title')
        self.assertIsNotNone(titletag)
        self.assertEquals(titletag.text, 'Website')


class TestLoad(unittest.TestCase):

    def runTest(self):
        command = "makejank --load \"js 'example/detail.js'\""
        sys.argv = shlex.split(command)

        result = capture_main_output()

        # Basic check
        soup = BeautifulSoup(result)
        children = list(soup.children)
        self.assertTrue(len(children) > 0)
        self.assertEquals(children[0].name, 'script')
