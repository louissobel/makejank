"""
tests renderer template processor
"""
import unittest
import tempfile

import jinja2

from makejank.environment import Environment
from makejank.dependency_detector import DependencyDetector, DependencyVisitor


class MockLoaderManager(object):

    def get_deps(self, env, loader_tag, args, kwargs):
        if loader_tag == 'ok':
            return set(['dep1', 'dep2'])
        elif loader_tag == 'recurs':
            return set(['rec1', 'dep1'])
        elif loader_tag == 'keyerror':
            raise KeyError
        elif loader_tag == 'typeerror':
            raise TypeError
        elif loader_tag == 'valueerror':
            raise ValueError
        elif loader_tag == 'syntaxerror':
            raise SyntaxError

env = Environment(rootdir='/')
env.loader_manager = MockLoaderManager()

# Tests the load_callback
class TestBasic(unittest.TestCase):
    def runTest(self):
        d = DependencyDetector(env)
        d.deps = set(['dep0'])
        d.load_callback('ok', None, None)
        self.assertEqual(d.deps, set([
            'dep0',
            'dep1',
            'dep2',
        ]))

class TestKeyErrorHandling(unittest.TestCase):
    """
    Turns a key error into a TypeError
    """
    def runTest(self):
        with self.assertRaises(TypeError):
            DependencyDetector(env).load_callback('keyerror', None, None)


class TestTypeErrorHandling(unittest.TestCase):
    """
    Propagates a TypeError
    """
    def runTest(self):
        with self.assertRaises(TypeError):
            DependencyDetector(env).load_callback('typeerror', None, None)


class TestValueErrorHandling(unittest.TestCase):
    """
    Propagates a ValueError
    """
    def runTest(self):
        with self.assertRaises(ValueError):
            DependencyDetector(env).load_callback('valueerror', None, None)


class TestSyntaxErrorHandling(unittest.TestCase):
    """
    Propagates a SyntaxError
    """
    def runTest(self):
        with self.assertRaises(SyntaxError):
            DependencyDetector(env).load_callback('syntaxerror', None, None)


# Test the embededded DependencyVisitor
class TestDependencyVisitor(unittest.TestCase):
    template_templates = [
        "{%% extends %s %%}",
        "{%% include %s %%}",
        "{%% import %s as b %%}",
        "{%% from %s import b %%}",
    ]

    def parse_and_visit_template(self, template):
        env = jinja2.Environment()
        tree = env.parse(template)
        visitor = DependencyVisitor()
        visitor.visit(tree)
        return visitor

    def test_works(self):
        """
        extends
        include
        import
        from import
        """
        template = """
        {% extends 'extended' %}
        {% include 'included' %}
        {% import 'imported' as b %}
        {% from 'importedfrom' import a %}
        """
        visitor = self.parse_and_visit_template(template)
        self.assertEquals(visitor.deps, set([
            'extended',
            'included',
            'imported',
            'importedfrom',
        ]))

    def test_catches_template_name(self):
        for template_template in self.template_templates:
            template = template_template % 'name'
            with self.assertRaises(ValueError):
                self.parse_and_visit_template(template)

    def test_catches_template_notstring(self):
        for template_template in self.template_templates:
            template = template_template % '9'
            with self.assertRaises(ValueError):
                self.parse_and_visit_template(template)


# Test the process method
class TestProcessSimple(unittest.TestCase):
    """
    Renders a template
    """
    def runTest(self):
        r = DependencyDetector(env).process("{% load ok %}")
        self.assertEquals(r, set(['dep1', 'dep2']))


class TestProcessRecursive(unittest.TestCase):
    """
    does a recursion.
    """
    def runTest(self):
        t = tempfile.NamedTemporaryFile()
        t.write("{% load recurs %}")
        t.flush()

        template = """
        {%% load ok %%}
        {%% include '%s' %%}
        """ % t.name
        r = DependencyDetector(env).process(template)
        self.assertEquals(r, set([
            'dep1',
            'dep2',
            'rec1',
            t.name,
        ]))


class TestProcessInfiniteRecursion(unittest.TestCase):
    """
    infinite recursion
    """
    def runTest(self):
        t = tempfile.NamedTemporaryFile()
        recursive_include = "{%% include '%s' %%}" % t.name
        t.write(recursive_include)
        t.flush()

        # TODO: for now, we bubble it as a runtime error
        with self.assertRaises(RuntimeError):
            r = DependencyDetector(env).process(recursive_include)
