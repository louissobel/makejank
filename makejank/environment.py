"""
class wrapping makejank environment
"""
import os
import os.path
import logging
logger = logging.getLogger(__name__)

from loader_manager import LoaderManager
from caches import NoopCache

from renderer import Renderer
from dependency_detector import DependencyDetector

class Environment(object):
    def __init__(self, rootdir, loaders=None, cache=None):
        self.rootdir = rootdir
        if not os.path.isabs(self.rootdir):
            raise ValueError("rootdir of environment must be absolute")

        self.loader_manager = LoaderManager(cache=cache)
        if loaders is not None:
            for l in loaders:
                self.loader_manager.register(l)

        self.cwd = os.getcwd()
        self.logger = logger

    def resolve_path(self, path):
        return os.path.join(self.rootdir, path)

    ## Rendering methods (publics)
    def render_string(self, string, get_deps=False):
        if get_deps:
            return DependencyDetector(self).process(string)
        else:
            return Renderer(self).process(string)

    def render_load_args(self, load_args, get_deps=False):
        template = "{% load " + load_args + " %}"
        return self.render_string(template, get_deps=get_deps)

    def render_template(self, template_filename, get_deps=False):
        if get_deps:
            deps = DependencyDetector(self).get_source_and_process(template_filename)
            deps.add(self.resolve_path(template_filename))
            return deps
        else:
            return Renderer(self).get_source_and_process(template_filename)
