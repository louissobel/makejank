import os
import os.path
import string
import random

randstring = lambda : ''.join(random.choice(string.letters) for _ in range(10))

class ForceImportFailure():
    def __init__(self, modules):
        self.modules = modules

    def find_module(self, fullname, path=None):
        if fullname in self.modules:
            raise ImportError('Debug import failure for %s' % fullname)


def nonexistent_filename():
    while True:
        filename = randstring()
        if not os.path.exists('/' + filename):
            break
    return filename

def datadir():
    thisdir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(thisdir, 'data')

def test_datafile(filename):
    return os.path.join(datadir(), filename)