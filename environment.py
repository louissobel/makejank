"""
class wrapping makejank environment
"""
import os.path

from renderer import Renderer
from dependency_detector import DependencyDetector


class Environment(object):
    def __init__(self, rootdir, loader_manager):
        self.rootdir = rootdir
        self.loader_manager = loader_manager

    def resolve_path(self, path):
        return os.path.join(self.rootdir, path)

    def render(self, template_filename):
        return Renderer(self).process(template_filename)

    def get_deps(self, template_filename):
        return DependencyDetector(self).process(template_filename)
