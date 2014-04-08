"""
Runs a makejank
"""
import unittest
import os
import os.path
import tempfile
import subprocess
import shutil

import makejank

class IntegrationTestMixin(object):

    def setUp(self):
        self.cwd = os.getcwd()
        self.tempdir = tempfile.mkdtemp()

        newd = os.path.join(
            os.path.dirname(os.path.abspath(makejank.__file__)),
            '..',
        )
        os.chdir(newd)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tempdir)


class TestJankfile(IntegrationTestMixin, unittest.TestCase):

    def runTest(self):
        command = "python -m makejank -j example/Jankfile --output-dir %s" % self.tempdir

        # use check output to capture
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        # Check it
        if not os.path.exists(os.path.join(self.tempdir, 'index.html')):
            raise AssertionError('index.html not created')

        if not os.path.exists(os.path.join(self.tempdir, 'detail.html')):
            raise AssertionError('detail.html not created')
