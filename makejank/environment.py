"""
class wrapping makejank environment
"""
import os
import os.path
import logging
logger = logging.getLogger(__name__)
import re

from loader_manager import LoaderManager
from caches import NoopCache
from loader_finder import LoaderFinder

from renderer import Renderer
from dependency_detector import DependencyDetector

USE_REGEX = re.compile(r'^(\w+)(?: from ([\w\.]+))?$')

class Environment(object):
    def __init__(self, rootdir, cache=None):
        self.rootdir = rootdir
        if not os.path.isabs(self.rootdir):
            raise ValueError("rootdir of environment must be absolute")

        self.loader_manager = LoaderManager(cache=cache)
        self.loader_finder = LoaderFinder()

        self.cwd = os.getcwd()
        self.logger = logger

    def resolve_path(self, path):
        return os.path.join(self.rootdir, path)

    def find_and_use_loader(self, loader_tag, from_package):
        """
        gets it from loader_finder and registers it with manager.
        from_package can be None.

        does NO error handling
        """
        l = self.loader_finder.find(loader_tag, from_package)
        self.loader_manager.register(l)

    def use_string(self, string):
        """
        Parse string like a use statement `a [from b[.c]*]`
        and send it to find_and_use_loader. Raises value error if bad string.
        """
        self.find_and_use_loader(*self._parse_use_string(string))

    def _parse_use_string(self, string):
        m = USE_REGEX.match(string)
        if not m:
            raise ValueError("Bad use string")
        else:
            return m.group(1), m.group(2)

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
