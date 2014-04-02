"""
Loader to load and parse a YAML file
"""
from . import BaseLoader

class YamlLoader(BaseLoader):

    tag = 'yaml'

    def __init__(self):
        try:
            import yaml
            self.yaml = yaml
        except ImportError:
            # TODO: what error?
            raise ValueError('yaml loader cannot find yaml module')

    def product(self, env, arg, kwargs):
        return None

    def dependencies(self, env, filename, kwargs):
        return set([env.resolve_path(filename)])

    def load(self, env, filename, kwargs):
        aswhat = kwargs.get('as')
        if aswhat is None:
            raise TypeError('as= is required argument to yaml loader')
        if not isinstance(aswhat, basestring):
            raise TypeError('as argument to yaml loader must be basestring')

        pathname = env.resolve_path(filename)
        try:
            with open(pathname) as f:
                data = self.yaml.load(f.read())
        except IOError as e:
            raise ValueError("Error reading file %s: %s" % (pathname, e.strerror))
        except self.yaml.YAMLError as e:
            raise ValueError("Malformed yaml in %s: %s" % (filename, e.message))

        return aswhat, data
