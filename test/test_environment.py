import unittest

from environment import Environment

class TestEnvironment(unittest.TestCase):

    def runTest(self):
        e = Environment('/a/b')
        self.assertEquals('/a/b/c', e.resolve_path('c'))
