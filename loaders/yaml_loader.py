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

    def load(self, env, args):
        filename, _, aswhat = args
        # filename 'as' aswhat
        # TODO should `aswhat` be optional?
        try:
            with open(env.resolve_path(filename)) as f:
                data = yaml.load(f.read())
        except IOError:
            # TODO: what do we do?
            raise ValueError("Unable To Find %s" % filename)
        except yaml.YAMLError as e:
            # TODO: WHAT DO WE DO?
            raise ValueError("Malformed yaml in %s (%s)" % (filename, str(e)))

        return aswhat, data