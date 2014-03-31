"""
Loader to load and parse a YAML file
"""
from . import BaseLoader

try:
    import yaml
except ImportError:
    HAVE_PYYAML = False
else:
    HAVE_PYYAML = True

class YamlLoader(BaseLoader):

    tag = 'yaml'

    def __init__(self):
        if not HAVE_PYYAML:
            # TODO: which error??
            raise ValueError

    def dependency_graph(self, env, args):
        filename = args[0]
        return None, set([env.resolve_path(filename)])

    def load(self, env, args):
        filename, _, aswhat = args
        # filename 'as' aswhat
        # TODO should `aswhat` be optional?

        pathname = env.resolve_path(filename)
        try:
            with open(pathname) as f:
                data = yaml.load(f.read())
        except IOError as e:
            raise ValueError("Error reading file %s: %s" % (pathname, e.strerror))
        except yaml.YAMLError as e:
            raise ValueError("Malformed yaml in %s: %s" % (filename, e.message))

        return aswhat, data
