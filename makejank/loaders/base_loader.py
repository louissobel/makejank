"""
Simple base loader
"""

def _deterministic_dict_string(d):
    """
    Returns a deterministic string representation of dict
    """
    parts = []
    for k in sorted(d.keys()):
        parts.append("%r:%r" % (k, d[k]))
    return '{%s}' % ','.join(parts)

class BaseLoader(object):

    CACHE_RESULT = True
    DIFFERENT_FOR_PRODUCTION = True

    def product(self, env, arg, kwargs):
        """
        A string uniquely identifying the product of this
        (for the cache). Return None for no-cache
        """
        if self.CACHE_RESULT:
            key = "%s:%s:%s" % (self.tag, arg, _deterministic_dict_string(kwargs))
            if self.DIFFERENT_FOR_PRODUCTION and env.production:
                key += ":p"
            return key
        else:
            return None

    def dependencies_product(self, env, arg, kwargs):
        """
        by default, tack on a `:dependencies` to the product
        But exists so that loaders can change if they want.

        product + ':dependencies' # TODO TODO TODO collisions :/
        """
        p = self.product(env, arg, kwargs)
        if p:
            p += ':dependencies'
        return p

    def dependencies(self, env, arg, kwargs):
        """
        Abstract. What dependencies does this have?
        """
        raise NotImplementedError

    def load(self, env, arg, kwargs):
        """
        Abstract. env is a environment.Environment object
        args is a list of arguments from jinja template
        """
        raise NotImplementedError
    