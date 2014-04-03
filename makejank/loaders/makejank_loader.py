
from makejank.renderer import Renderer
from makejank.dependency_detector import DependencyDetector

from . import BaseLoader

PRODUCT_NAME_TEMPLATE = "%s:makejank"

class MakejankLoader(BaseLoader):

    tag = 'makejank'

    def product(self, env, filename, kwargs):
        return PRODUCT_NAME_TEMPLATE % filename

    def dependencies(self, env, filename, kwargs):
        return DependencyDetector(env).get_source_and_process(filename)

    def load(self, env, filename, kwargs):
        return Renderer(env).get_source_and_process(filename)
