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


class TestProduct(unittest.TestCase):
    def runTest(self):
        loader = YamlLoader()
        self.assertIsNone(loader.product(env, 'foobar', {}))


class TestDependecies(unittest.TestCase):
    def runTest(self):
        loader = YamlLoader()
        self.assertEquals(loader.dependencies(env, 'foobar', {}), set([
            env.resolve_path('foobar')
        ]))


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

class TestCannotFindFile(unittest.TestCase):

    def runTest(self):
        loader = YamlLoader()
        filename = test.helpers.nonexistent_filename()

        arg = filename
        kwargs = {'as':'data'}
        with self.assertRaises(ValueError) as e:
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

class TestNoYaml(unittest.TestCase):
    """
    Tests for case of no `yaml` present
    """

    def runTest(self):
        del sys.modules['yaml']
        self.fail_yaml = test.helpers.ForceImportFailure(['yaml'])
        sys.meta_path.append(self.fail_yaml)

        import makejank.loaders.yaml_loader
        reload(makejank.loaders.yaml_loader)
        with self.assertRaises(ValueError):
            makejank.loaders.yaml_loader.YamlLoader()

        sys.meta_path.remove(self.fail_yaml)
        reload(makejank.loaders.yaml_loader)

