"""
Tests a bunch of different command line option
combinations to get errors and expected
"""
import os
import unittest
import tempfile
import shutil

from makejank import main

def null_except(**kwargs):
    """
    null kwargs config except that given
    """
    out = {
        'cache_dir': None,
        'base_dir': None,
        'mode': None,
        'source': None,
        'load': None,
        'output_dir': None,
        'jankfile': None,
        'target': None,
        'deps': False,
    }
    for k, v in kwargs.items():
        if not k in out:
            raise AssertionError("%s not a key" % k)
        out[k] = v
    return out


def run(argstring):
    parser = main.get_parser()
    args = parser.parse_args(argstring.split(' '))
    return main.get_kwargs(args, parser)

def print_dict(s):
    for k in sorted(s.keys()):
        print k, ":", s[k]

class FreshCwdMixin(object):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp(dir=os.getcwd())
        self.olddir = os.getcwd()
        os.chdir(self.tempdir)

    def tearDown(self):
        os.chdir(self.olddir)
        shutil.rmtree(self.tempdir)


class TestJankMode(unittest.TestCase, FreshCwdMixin):
    """
    basic.
    """
    def setUp(self):
        FreshCwdMixin.setUp(self)
        # write a DEFAULT_JANKFILE_NAME file
        with open(main.DEFAULT_JANKFILE_NAME, 'w') as f:
            pass

    def runTest(self):
        result = run("")
        expected = null_except(
            jankfile={},
            base_dir=self.tempdir,
            cache_dir=os.path.join(self.tempdir, main.DEFAULT_CACHE_DIR),
            output_dir=os.path.join(self.tempdir, main.DEFAULT_OUTPUT_DIR),
            mode=main.JANKMODE,
        )
        self.assertEquals(result, expected)

    def tearDown(self):
        FreshCwdMixin.tearDown(self)


class TestSourceMode(unittest.TestCase, FreshCwdMixin):
    """
    basic.
    """
    def setUp(self):
        FreshCwdMixin.setUp(self)

    def runTest(self):
        result = run("abc")
        expected = null_except(
            jankfile={},
            base_dir=self.tempdir,
            cache_dir=os.path.join(self.tempdir, main.DEFAULT_CACHE_DIR),
            mode=main.SOURCEMODE,
            source='abc',
        )
        self.assertEquals(result, expected)

    def tearDown(self):
        FreshCwdMixin.tearDown(self)


class TestLoadMode(unittest.TestCase, FreshCwdMixin):
    """
    basic.
    """
    def setUp(self):
        FreshCwdMixin.setUp(self)

    def runTest(self):
        result = run("--load abc")
        expected = null_except(
            jankfile={},
            base_dir=self.tempdir,
            cache_dir=os.path.join(self.tempdir, main.DEFAULT_CACHE_DIR),
            mode=main.LOADMODE,
            load='abc',
        )
        self.assertEquals(result, expected)

    def tearDown(self):
        FreshCwdMixin.tearDown(self)