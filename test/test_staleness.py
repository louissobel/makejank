import unittest
import tempfile
import os

import staleness

import test.helpers

class TestNotStale(unittest.TestCase):
    def runTest(self):
        dep1 = tempfile.NamedTemporaryFile()
        dep2 = tempfile.NamedTemporaryFile()

        os.utime(dep1.name, (5, 5))
        os.utime(dep2.name, (6, 6))
        self.assertIs(staleness.is_stale(10, [dep1.name, dep2.name]), False)

class TestStale(unittest.TestCase):
   def runTest(self):
          dep1 = tempfile.NamedTemporaryFile()
          dep2 = tempfile.NamedTemporaryFile()

          self.assertIs(staleness.is_stale(5, [dep1.name, dep2.name]), True)

class TestStaleOne(unittest.TestCase):
   def runTest(self):
        dep1 = tempfile.NamedTemporaryFile()
        dep2 = tempfile.NamedTemporaryFile()

        os.utime(dep1.name, (1, 1))
        self.assertIs(staleness.is_stale(5, [dep1.name, dep2.name]), True)

class TestOneDepNotStale(unittest.TestCase):
    def runTest(self):
        dep = tempfile.NamedTemporaryFile()
        os.utime(dep.name, (5, 5))
        self.assertIs(staleness.is_stale(10, [dep.name]), False)

class TestOneDepStale(unittest.TestCase):
    def runTest(self):
        dep = tempfile.NamedTemporaryFile()
        self.assertIs(staleness.is_stale(10, [dep.name]), True)

class TestDepGreaterThanOrEqual(unittest.TestCase):
    """
    if there is a tie, we call it stales
    """
    def runTest(self):
        dep = tempfile.NamedTemporaryFile()
        os.utime(dep.name, (10, 10))
        self.assertIs(staleness.is_stale(10, [dep.name]), True)

class TestNoDeps(unittest.TestCase):
    def runTest(self):
        self.assertIs(staleness.is_stale(10, []), False)
        self.assertIs(staleness.is_stale(10000000000, []), False)

class TestMissingDeps(unittest.TestCase):
    def runTest(self):
        nondep = '/' + test.helpers.nonexistent_filename()
        self.assertIs(staleness.is_stale(10000000, [nondep]), True)

class TestNonAbsoluteDep(unittest.TestCase):
    def runTest(self):
        with self.assertRaises(TypeError):
            staleness.is_stale(100, ['/sf', 'df'])

class TestNoneProductLastModified(unittest.TestCase):
    def runTest(self):
        self.assertIs(staleness.is_stale(None, []), True)
