"""
Runs a makejank

Doesnt actually shell out, rather, fakes sys.argv and calls main.main
"""
import unittest
import os
import sys
import os.path
import tempfile
import subprocess
import shutil

from makejank import main

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
