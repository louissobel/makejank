from . import BaseLoader

PRODUCT_NAME_TEMPLATE = "%s:makejank"

class MakejankLoader(BaseLoader):

    tag = 'makejank'

    def dependency_graph(self, env, args):
        filename = args[0]
        deps = env.get_deps(filename)
        product = PRODUCT_NAME_TEMPLATE % filename
        return product, deps

    def load(self, env, args):
        filename = args[0]
        return env.render(filename)
