"""
Write a YAML file, call the loader, check that it works
"""
import unittest
import tempfile
import sys

from makejank.environment import Environment
from makejank.loaders import YamlLoader

import test.helpers

good_yaml = """
a: hello
b:
 - 1
 - 2
 - 3
"""

good_yaml_expected = {
    'a': 'hello',
    'b': [1, 2, 3]
}

env = Environment(rootdir='/')


class TestOK(unittest.TestCase):

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()
        self.tempfile.write(good_yaml)
        self.tempfile.flush()

    def runTest(self):
        loader = YamlLoader()
        arg = self.tempfile.name
        kwargs = {'as':'foobee'}
        expected = ('foobee', good_yaml_expected)
        result = loader.load(env, arg, kwargs)
        self.assertEquals(result, expected)


class TestNoAs(TestOK):
    def runTest(self):
        loader = YamlLoader()
        arg = self.tempfile.name
        with self.assertRaises(TypeError):
            loader.load(env, arg, {})


class TestBadAs(TestOK):
    def runTest(self):
        loader = YamlLoader()
        arg = self.tempfile.name
        kwargs = {'as':8}
        with self.assertRaises(TypeError):
            loader.load(env, arg, kwargs)


class TestMalformedYaml(unittest.TestCase):

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()
        self.tempfile.write("@  bleep>dfsdsfsdf:;")
        self.tempfile.flush()

    def runTest(self):
        loader = YamlLoader()
        arg = self.tempfile.name
        kwargs = {'as':'data'}
        with self.assertRaises(ValueError):
            loader.load(env, arg, kwargs)

