"""
Write a YAML file, call the loader, check that it works
"""
import unittest
import tempfile
import sys

import environment
from loaders import YamlLoader

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

env = environment.Environment(rootpath='/')

class TestOK(unittest.TestCase):

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()
        self.tempfile.write(good_yaml)
        self.tempfile.flush()

    def runTest(self):
        loader = YamlLoader()
        args = [self.tempfile.name, 'as', 'foobee']
        expected = ('foobee', good_yaml_expected)
        result = loader.load(env, args)
        self.assertEquals(result, expected)


class TestCannotFindFile(unittest.TestCase):

    def runTest(self):
        loader = YamlLoader()
        filename = test.helpers.nonexistent_filename()

        args = [filename, 'as', 'data']
        with self.assertRaises(ValueError) as e:
            loader.load(env, args)

class TestMalformedYaml(unittest.TestCase):

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()
        self.tempfile.write("@  bleep>dfsdsfsdf:;")
        self.tempfile.flush()

    def runTest(self):
        loader = YamlLoader()
        args = [self.tempfile.name, 'as', 'foobee']
        with self.assertRaises(ValueError):
            loader.load(env, args)

class TestNoYaml(unittest.TestCase):
    """
    Tests for case of no `yaml` present
    """

    def runTest(self):
        del sys.modules['yaml']
        self.fail_yaml = test.helpers.ForceImportFailure(['yaml'])
        sys.meta_path.append(self.fail_yaml)

        import loaders.yaml_loader
        reload(loaders.yaml_loader)
        with self.assertRaises(ValueError):
            loaders.yaml_loader.YamlLoader()

        sys.meta_path.remove(self.fail_yaml)
        reload(loaders.yaml_loader)

