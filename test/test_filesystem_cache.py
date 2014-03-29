"""
Special tests for filesystem cache
"""
import unittest
import tempfile
import os
import os.path
import shutil
import stat

from caches import FilesystemCache

import test.helpers

DIR_READ_ONLY = stat.S_IROTH | stat.S_IRUSR | stat.S_IRGRP

class TestCreatesDirectory(unittest.TestCase):
    """
    Make sure that it creates the directory if it does not exist.
    """
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.cachedir = os.path.join(self.tempdir, 'cachedir')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def runTest(self):
        c = FilesystemCache(self.cachedir)
        c.put('a', 'b')
        self.assertEquals(c.get('a'), 'b')


class TestInitFailsIfCannotCreate(unittest.TestCase):
    """
    Init should fail if we cannot create the cachedir
    """
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        os.chmod(self.tempdir, DIR_READ_ONLY)
        self.cachedir = os.path.join(self.tempdir, 'cachedir')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def runTest(self):
        with self.assertRaises(ValueError):
            FilesystemCache(self.cachedir)


class TestInitFailsIfWouldOverwriteFile(unittest.TestCase):
    """
    Init should fail if there is already a file named cachedir
    """
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        os.open(os.path.join(self.tempdir, 'cachedir'), os.O_CREAT)
        self.cachedir = os.path.join(self.tempdir, 'cachedir')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def runTest(self):
        with self.assertRaises(ValueError):
            FilesystemCache(self.cachedir)

class TestInitFailsIfCannotWrite(unittest.TestCase):
    """
    test that if we cannot write to our cachedir, fail
    """
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.cachedir = os.path.join(self.tempdir, 'cachedir')
        os.mkdir(self.cachedir, DIR_READ_ONLY) # path, mode

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def runTest(self):
        with self.assertRaises(ValueError):
            FilesystemCache(self.cachedir)


class TestAbsPathRequired(unittest.TestCase):
    """
    check that it will fail if not given absolute path
    """
    def runTest(self):
        with self.assertRaises(ValueError):
            FilesystemCache('notrelative')