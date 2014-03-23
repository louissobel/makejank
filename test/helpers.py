import os
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