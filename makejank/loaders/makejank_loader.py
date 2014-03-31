
from makejank.renderer import Renderer
from makejank.dependency_detector import DependencyDetector

from . import BaseLoader

PRODUCT_NAME_TEMPLATE = "%s:makejank"

class MakejankLoader(BaseLoader):

    tag = 'makejank'

    def product(self, env, args):
        filename = args[0]
        return PRODUCT_NAME_TEMPLATE % filename

    def dependencies(self, env, args):
        filename = args[0]
        return DependencyDetector(env).process(filename)

    def load(self, env, args):
        filename = args[0]
        return Renderer(env).process(filename)
