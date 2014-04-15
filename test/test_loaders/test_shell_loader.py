"""
basic shell loader
"""
import unittest

from makejank.environment import Environment
from makejank.loaders import ShellLoader

env = Environment(rootdir='/')


# Dependencies
class TestNoDeps(unittest.TestCase):
    def runTest(self):
        l = ShellLoader()
        r = l.dependencies(env, "echo 'hi'", {})
        self.assertEquals(r, set())


class TestOneDep(unittest.TestCase):
    def runTest(self):
        l = ShellLoader()
        r = l.dependencies(env, "echo 'hi'", {'depends_on':['foo']})
        self.assertEquals(r, set([
            env.resolve_path('foo')
        ]))


class TestMultipleDeps(unittest.TestCase):
    def runTest(self):
        l = ShellLoader()
        r = l.dependencies(env, "echo 'hi'", {'depends_on':['foo', '/bar']})
        self.assertEquals(r, set([
            env.resolve_path('foo'),
            '/bar',
        ]))


# Shell
class TestSimple(unittest.TestCase):
    def runTest(self):
        l = ShellLoader()
        r = l.load(env, "echo 'hi'", {})
        self.assertEquals(r, 'hi\n')


class TestShlex(unittest.TestCase):
    def runTest(self):
        l = ShellLoader()
        command = "python -c 'b = 2 **5; print \"%d\" % b'"
        r = l.load(env, command, {})
        self.assertEquals(r, '32\n')


class TestCommandNotFound(unittest.TestCase):
    def runTest(self):
        l = ShellLoader()
        with self.assertRaises(SyntaxError):
            r = l.load(env, "dfasdfsadfsdfsdfsdfasd", {}) # hopefully not a command :/


class TestCommandFail(unittest.TestCase):
    def runTest(self):
        l = ShellLoader()
        command = "python -c 'import sys; sys.exit(1)'"
        with self.assertRaises(ValueError):
            r = l.load(env, command, {})


class TestTimeout(unittest.TestCase):
    def runTest(self):
        l = ShellLoader()
        with self.assertRaisesRegexp(ValueError, r"^Process"):
            r = l.load(env, "yes", {'timeout':.25})


class TestTimeoutCatchingSigTerm(unittest.TestCase):
    def runTest(self):
        """
        use a sigkill when sigterm doesn't work
        """
        l = ShellLoader()
        command = "python -c 'import signal; signal.signal(signal.SIGTERM, signal.SIG_IGN); import time; time.sleep(2)'"
        with self.assertRaisesRegexp(ValueError, r"^Process"):
            r = l.load(env, command, {'timeout':.25})


class TestPipes(unittest.TestCase):
    def runTest(self):
        """
        this is bash; use a pipe
        """
        l = ShellLoader()
        command = "yes foo | head -10"
        r = l.load(env, command, {})
        self.assertEquals(r, '\n'.join(["foo"]*10) + "\n")
