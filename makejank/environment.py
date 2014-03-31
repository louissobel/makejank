"""
class wrapping makejank environment
"""
import os.path

from loader_manager import LoaderManager
from caches import NoopCache


class Environment(object):
    def __init__(self, rootdir, loaders=None, cache=None):
        self.rootdir = rootdir
        if not os.path.isabs(self.rootdir):
            raise ValueError("rootdir of environment must be absolute")

        self.loader_manager = LoaderManager(cache=cache)
        if loaders is not None:
            for l in loaders:
                self.loader_manager.register(l)

    def resolve_path(self, path):
        return os.path.join(self.rootdir, path)
