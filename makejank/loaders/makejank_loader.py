
from makejank.renderer import Renderer
from makejank.dependency_detector import DependencyDetector

from . import BaseLoader

class MakejankLoader(BaseLoader):

    tag = 'makejank'

    def dependencies(self, env, filename, kwargs):
        deps = DependencyDetector(env).get_source_and_process(filename)
        # Include myself!
        deps.add(env.resolve_path(filename))
        return deps

    def load(self, env, filename, kwargs):
        return Renderer(env).get_source_and_process(filename)
