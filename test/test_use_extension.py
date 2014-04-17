"""
Tests jinja2 use extension
"""
import unittest

import jinja2

from makejank import jinja_extensions

class _GetUsesTemplateProcessor(object):
    """
    Janky version of template_processor.TemplateProcessor
    """

    def __init__(self):
        self.jinja_env = jinja2.Environment(
            extensions=[jinja_extensions.UseExtension],
        )

        self.jinja_env.makejank_use_callback = self.use_callback

        self.uses = []

    def use_callback(self, *args, **kwargs):
        self.uses.append((args, kwargs))

    def process(self, template_string):
        self.jinja_env.parse(template_string)
        return self.uses


class _ErrorRaisingTemplateProcessor(_GetUsesTemplateProcessor):
    """
    Blows up with error_klass passed on use
    """
    def __init__(self, error_klass):
        _GetLoadsTemplateProcessor.__init__(self)
        self.error_klass = error_klass

    def use_callback(self, *args, **kwargs):
        raise self.error_klass("ERROR")

def parse_uses(string):
    return _GetUsesTemplateProcessor().process(string)

def test_GetUsesTemplateProcessor():
    assert parse_uses('') == []


class TestSimple(unittest.TestCase):
    def runTest(self):
        r = parse_uses('{% use foo %}')
        self.assertEquals(r, [(('foo', None), {})])


class TestFrom(unittest.TestCase):
    def runTest(self):
        r = parse_uses('{% use foo from bar %}')
        self.assertEquals(r, [(('foo', 'bar'), {})])


class TestFromDotted(unittest.TestCase):
    def runTest(self):
        r = parse_uses('{% use foo from bar.ha.wow %}')
        self.assertEquals(r, [(('foo', 'bar.ha.wow'), {})])


class TestBadLoaderTag(unittest.TestCase):
    def runTest(self):
        with self.assertRaises(jinja2.TemplateSyntaxError):
            parse_uses('{% use "foo" %}')


class TestMissingFrom(unittest.TestCase):
    def runTest(self):
        with self.assertRaises(jinja2.TemplateSyntaxError):
            parse_uses('{% use foo a.b %}')


class TestWrongNameFrom(unittest.TestCase):
    def runTest(self):
        with self.assertRaises(jinja2.TemplateSyntaxError):
            parse_uses('{% use foo form a %}')


class TestMissingFromArg(unittest.TestCase):
    def runTest(self):
        with self.assertRaises(jinja2.TemplateSyntaxError):
            parse_uses('{% use foo from %}')


class TestBadFromPackage(unittest.TestCase):
    def runTest(self):
        with self.assertRaises(jinja2.TemplateSyntaxError):
            parse_uses('{% use foo from 9 %}')
