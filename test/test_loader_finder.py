"""
loader finder


"""
import unittest
import sys

from makejank.loader_finder import LoaderFinder
from makejank.loaders import ShellLoader
from makejank.loaders import BaseLoader

class MockLoaderModule(object):

    class loader(BaseLoader):
        youfoundme = True


class MockLoaderModuleMissingLoader(object):
    pass


class MockLoaderModuleBadLoader(object):

    class loader(object):
        """
        not a BaseLoader
        """
        pass


class TestStdlib(unittest.TestCase):
    """
    get the shell loader from stdlib
    """
    def runTest(self):
        lf = LoaderFinder()
        l = lf.find('shell')
        self.assertIsInstance(l, ShellLoader)


class TestFrom(unittest.TestCase):
    """
    get the shell loader specifying from
    """
    def runTest(self):
        lf = LoaderFinder()
        l = lf.find('shell', from_package='makejank.loaders')


class TestImport(unittest.TestCase):
    """
    will do a naked import
    """
    def runTest(self):
        sys.modules['makejank_mock'] = MockLoaderModule()
        lf = LoaderFinder()
        l = lf.find('mock')
        self.assertTrue(l.youfoundme)


class TestCannotImport(unittest.TestCase):
    def runTest(self):
        lf = LoaderFinder()
        with self.assertRaises(ValueError):
            lf.find('idjflkasjdfsadjfhsadkjfasdkjflsdkjf')


class TestCannotImportFrom(unittest.TestCase):
    def runTest(self):
        lf = LoaderFinder()
        with self.assertRaises(ValueError):
            lf.find('fdsfsdfasdf', from_package='makejank')


class TestModuleMissingAttribute(unittest.TestCase):
    def runTest(self):
        lf = LoaderFinder()
        sys.modules['makejank_mock'] = MockLoaderModuleMissingLoader()
        with self.assertRaisesRegexp(ValueError, 'attribute'):
            lf.find('mock')


class TestLoaderNotBaseLoader(unittest.TestCase):
    def runTest(self):
        lf = LoaderFinder()
        sys.modules['makejank_mock'] = MockLoaderModuleBadLoader()
        with self.assertRaisesRegexp(ValueError, 'BaseLoader'):
            lf.find('mock')