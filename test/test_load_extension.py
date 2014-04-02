"""
Tests jinja2 load extension
"""
import unittest

import jinja2

from makejank import jinja_extensions

class _GetLoadsTemplateProcessor(object):
    """
    Janky version of template_processor.TemplateProcessor
    """

    def __init__(self):
        self.jinja_env = jinja2.Environment(
            extensions=[jinja_extensions.LoadExtension],
        )

        self.jinja_env.makejank_load_callback = self.load_callback

        self.loads = []

    def load_callback(self, *args, **kwargs):
        self.loads.append((args, kwargs))

    def process(self, template_string):
        self.jinja_env.parse(template_string)
        return self.loads


class _ErrorRaisingTemplateProcessor(_GetLoadsTemplateProcessor):
    """
    Blows up with error_klass passed on load
    """
    def __init__(self, error_klass):
        _GetLoadsTemplateProcessor.__init__(self)
        self.error_klass = error_klass

    def load_callback(self, *args, **kwargs):
        raise self.error_klass("ERROR")

def parse_loads(string):
    return _GetLoadsTemplateProcessor().process(string)

def test_GetLoadsTemplateProcessor():
    assert parse_loads('') == []


class TestBasic(unittest.TestCase):
    def runTest(self):
        template = '{% load a b %}'
        loads = parse_loads(template)
        self.assertEquals(loads,[
            (('a', ['b']), {})
        ])


class TestStringArg(unittest.TestCase):
    def runTest(self):
        template = '{% load a "b" %}'
        loads = parse_loads(template)
        self.assertEquals(loads,[
            (('a', ['b']), {})
        ])


class TestMoreArgs(unittest.TestCase):
    def runTest(self):
        template = '{% load a b "c" d "e" f g %}'
        loads = parse_loads(template)
        self.assertEquals(loads,[
            (('a', ['b', 'c', 'd', 'e', 'f', 'g']), {})
        ])


class TestNaughtyLoadType(unittest.TestCase):
    def runTest(self):
        """load type must be bare name"""
        template = '{% load "a" %}'
        with self.assertRaises(jinja2.TemplateSyntaxError):
            parse_loads(template)


class TestNaughtyAdditionalArg(unittest.TestCase):
    def runTest(self):
        template = '{% load a a.b  %}'
        with self.assertRaises(jinja2.TemplateSyntaxError):
            parse_loads(template)


class TestValueErrorHandling(unittest.TestCase):
    def runTest(self):
        template = '{% load a b %}'
        with self.assertRaises(jinja2.TemplateAssertionError):
            _ErrorRaisingTemplateProcessor(ValueError).process(template)


class TestTypeErrorHandling(unittest.TestCase):
    def runTest(self):
        template = '{% load a b %}'
        with self.assertRaises(jinja2.TemplateAssertionError):
            _ErrorRaisingTemplateProcessor(TypeError).process(template)


class TestSyntaxErrorHandling(unittest.TestCase):
    def runTest(self):
        template = '{% load a b %}'
        with self.assertRaises(jinja2.TemplateSyntaxError):
            _ErrorRaisingTemplateProcessor(SyntaxError).process(template)
