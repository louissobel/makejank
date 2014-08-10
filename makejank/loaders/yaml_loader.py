"""
Loader to load and parse a YAML file
"""
from . import FileLoader, LoaderWrappingLoader

class YamlLoader(LoaderWrappingLoader):

    tag = 'yaml'
    WRAPPED_LOADER = FileLoader()
    CACHE_RESULT = False

    def __init__(self):
        try:
            import yaml
            self.yaml = yaml
        except ImportError:
            # TODO: what error?
            raise ValueError('yaml loader cannot find yaml module')

    def wrap_result(self, env, filename, kwargs, result):
        aswhat = kwargs.get('as')
        if aswhat is None:
            raise TypeError('as= is required argument to yaml loader')
        if not isinstance(aswhat, basestring):
            raise TypeError('as argument to yaml loader must be basestring')

        try:
            data = self.yaml.load(result)
        except self.yaml.YAMLError as e:
            msg = "Malformed yaml in %s: %s" % (filename, e.message)
            env.logger.error(msg)
            raise ValueError(msg)

        return aswhat, data
