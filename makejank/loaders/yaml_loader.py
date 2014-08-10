"""
Loader to load and parse a YAML file
"""
import yaml

from . import FileLoader, LoaderWrappingLoader

class YamlLoader(LoaderWrappingLoader):

    tag = 'yaml'
    WRAPPED_LOADER = FileLoader()
    CACHE_RESULT = False
    DIFFERENT_FOR_PRODUCTION = False

    def wrap_result(self, env, filename, kwargs, result):
        aswhat = kwargs.get('as')
        if aswhat is None:
            raise TypeError('as= is required argument to yaml loader')
        if not isinstance(aswhat, basestring):
            raise TypeError('as argument to yaml loader must be basestring')

        try:
            data = yaml.load(result)
        except yaml.YAMLError as e:
            msg = "Malformed yaml in %s: %s" % (filename, e.message)
            env.logger.error(msg)
            raise ValueError(msg)

        return aswhat, data
