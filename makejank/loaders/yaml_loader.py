"""
Loader to load and parse a YAML file
"""
from . import FileLoader

class YamlLoader(FileLoader):

    tag = 'yaml'

    CACHE_RESULT = False

    def __init__(self):
        try:
            import yaml
            self.yaml = yaml
        except ImportError:
            # TODO: what error?
            raise ValueError('yaml loader cannot find yaml module')

    def load(self, env, filename, kwargs):
        aswhat = kwargs.get('as')
        if aswhat is None:
            raise TypeError('as= is required argument to yaml loader')
        if not isinstance(aswhat, basestring):
            raise TypeError('as argument to yaml loader must be basestring')

        contents = FileLoader.load(self, env, filename, kwargs)

        try:
            data = self.yaml.load(contents)
        except self.yaml.YAMLError as e:
            raise ValueError("Malformed yaml in %s: %s" % (filename, e.message))

        return aswhat, data
