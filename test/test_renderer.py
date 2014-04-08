"""
tests renderer template processor
"""
import unittest

import jinja2

from makejank.environment import Environment
from makejank.renderer import Renderer


class MockLoaderManager(object):

    def service(self, env, loader_tag, args, kwargs):
        if loader_tag == 'ok':
            return 'ok'
        elif loader_tag == 'tuple':
            return ('data', 'value')
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
        r = Renderer(env).load_callback('ok', None, None)
        self.assertIsInstance(r, jinja2.nodes.Output)
        self.assertEquals(len(r.nodes), 1)
        self.assertIsInstance(r.nodes[0], jinja2.nodes.Const)
        self.assertEquals(r.nodes[0].value, 'ok')


class TestAssign(unittest.TestCase):
    """
    Checks that a tuple becomes an Assign Node
    """
    def runTest(self):
        r = Renderer(env).load_callback('tuple', None, None)
        self.assertIsInstance(r, jinja2.nodes.Assign)
        self.assertIsInstance(r.target, jinja2.nodes.Name)
        self.assertEquals(r.target.name, 'data')
        self.assertEquals(r.target.ctx, 'store')
        self.assertIsInstance(r.node, jinja2.nodes.Const)
        self.assertEquals(r.node.value, 'value')


class TestKeyErrorHandling(unittest.TestCase):
    """
    Turns a key error into a TypeError
    """
    def runTest(self):
        with self.assertRaises(TypeError):
            Renderer(env).load_callback('keyerror', None, None)


class TestTypeErrorHandling(unittest.TestCase):
    """
    Propagates a TypeError
    """
    def runTest(self):
        with self.assertRaises(TypeError):
            Renderer(env).load_callback('typeerror', None, None)


class TestValueErrorHandling(unittest.TestCase):
    """
    Propagates a ValueError
    """
    def runTest(self):
        with self.assertRaises(ValueError):
            Renderer(env).load_callback('valueerror', None, None)


class TestSyntaxErrorHandling(unittest.TestCase):
    """
    Propagates a SyntaxError
    """
    def runTest(self):
        with self.assertRaises(SyntaxError):
            Renderer(env).load_callback('syntaxerror', None, None)

# Test the process method
class TestProcess(unittest.TestCase):
    """
    Renders a template
    """
    def runTest(self):
        r = Renderer(env).process("{% load ok %}")
        self.assertEquals(r, 'ok')
