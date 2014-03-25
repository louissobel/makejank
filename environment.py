"""
class wrapping makejank environment
"""
import os.path

from loader_manager import LoaderManager
from caches import NoopCache

from renderer import Renderer
from dependency_detector import DependencyDetector


class Environment(object):
    def __init__(self, rootdir, loaders=None, cache=None):
        self.rootdir = rootdir
        # TODO: enforce rootdir being abspath

        self.loader_manager = LoaderManager(cache=cache)
        if loaders is not None:
            for l in loaders:
                self.loader_manager.register(l)

    def resolve_path(self, path):
        return os.path.join(self.rootdir, path)

    def render(self, template_filename):
        return Renderer(self).process(template_filename)

    def get_deps(self, template_filename):
        return DependencyDetector(self).process(template_filename)
