"""
Simple base loader
"""

class BaseLoader(object):

    def product(self, env, args, kwargs):
        """
        Abstract. A string uniquely identifying the product of this
        (for the cache). Return None for no-cache
        """
        raise NotImplemented

    def dependencies(self, env, args, kwargs):
        """
        Abstract. What dependencies does this have?
        """
        raise NotImplemented

    def load(self, env, args, kwargs):
        """
        Abstract. env is a environment.Environment object
        args is a list of arguments from jinja template
        """
        raise NotImplemented
    