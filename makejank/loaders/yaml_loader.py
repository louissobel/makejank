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

    def product(self, env, args):
        return None

    def dependencies(self, env, args):
        filename = args[0]
        return set([env.resolve_path(filename)])

    def load(self, env, args):
        filename, _, aswhat = args
        # filename 'as' aswhat
        # TODO should `aswhat` be optional?

        pathname = env.resolve_path(filename)
        try:
            with open(pathname) as f:
                data = self.yaml.load(f.read())
        except IOError as e:
            raise ValueError("Error reading file %s: %s" % (pathname, e.strerror))
        except self.yaml.YAMLError as e:
            raise ValueError("Malformed yaml in %s: %s" % (filename, e.message))

        return aswhat, data
