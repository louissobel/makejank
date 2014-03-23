"""
class wrapping makejank environment
"""
import os.path

class Environment(object):
    def __init__(self, rootpath):
        self.rootpath = rootpath

    def resolve_path(self, path):
        return os.path.join(self.rootpath, path)