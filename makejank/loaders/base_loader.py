"""
Simple base loader
"""

class BaseLoader(object):

    def dependency_graph(self, env, args):
        """
        Default to Signaling a Nocache by returning None product.
        And, specify no deps.
        """
        return None, set()

    def load(self, env, args):
        """
        Abstract. env is a environment.Environment object
        args is a list of arguments from jinja template
        """
        raise NotImplemented
    