import unittest

from environment import Environment

import test.helpers

class TestEnvironmentResolvePath(unittest.TestCase):

    def runTest(self):
        e = Environment(rootdir='/a/b')
        self.assertEquals('/a/b/c', e.resolve_path('c'))

