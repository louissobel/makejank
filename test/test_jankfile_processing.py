"""
test a jankfile
"""
import unittest
import tempfile
import shutil
import os.path

from makejank import jankfile_processing

class MockEnv(object):

    # For logging, doesn't matter what it is right now
    cwd = '/'

    # Just the methods needed to stub jankfile_processing
    def render_load_args(self, string):
        return string


class JankfileProcessingMixin(object):
    FILES = [('foo', 'a'), ('bar', 'b')]

    def setUp(self):
        self.output_tempdir = tempfile.mkdtemp()

        self.env = MockEnv()

    def tearDown(self):
        shutil.rmtree(self.output_tempdir)

    def assertOutputFileContents(self, filename, contents):
        try:
            with open(os.path.join(self.output_tempdir, filename), 'r') as f:
                self.assertEquals(f.read(), contents)
        except IOError as e:
            raise AssertionError("Unable to read %s: %s" % (filename, e.message))


class TestProcessJankfile(JankfileProcessingMixin, unittest.TestCase):
    """
    Tests the processing of a jankfile
    """

    def runTest(self):
        jankfile = {
            'targets': {
                'foo': "a",
                'bar': "b",
            },
        }

        jankfile_processing.process_jankfile(self.env, jankfile, self.output_tempdir)

        # Assert they got there!
        for fn, c in self.FILES:
            self.assertOutputFileContents(fn, c)


class TestProcessJankfileSingleTarget(JankfileProcessingMixin, unittest.TestCase):
    """
    tests a jankfile with just one file
    """
    def runTest(self):
        jankfile = {
            'targets': {
                'foo': "a",
            },
        }

        jankfile_processing.process_jankfile(self.env, jankfile, self.output_tempdir)

        self.assertOutputFileContents('foo', 'a')


class TestJankfileNoTargetList(JankfileProcessingMixin, unittest.TestCase):
    """
    We should be OK with no targets in jankfile
    """
    def runTest(self):
        jankfile = {}
        jankfile_processing.process_jankfile(self.env, jankfile, self.output_tempdir)

class TestJankfileNoTargets(JankfileProcessingMixin, unittest.TestCase):
    """
    We should be OK with no targets specified
    """
    def runTest(self):
        jankfile = {'targets':{}}
        jankfile_processing.process_jankfile(self.env, jankfile, self.output_tempdir)
