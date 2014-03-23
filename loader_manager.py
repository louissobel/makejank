"""
Manages a set of loaders.
Finding them, and passing data to them
service method takes care of cacheing?
"""
import jinja2

class LoaderManager(object):

    def __init__(self):
        self.loaders = {}

    def register(self, loader):
        self.loaders[loader.tag] = loader

    def get_loader(self, loader_tag):
        loader = self.loaders.get(loader_tag)
        if loader is None:
            raise KeyError("Cannot find loader with tag %s" % loader_tag)
        else:
            return loader

    def service(self, env, loader_tag, args):
        loader = self.get_loader(loader_tag) # Raises KeyError.
        # do cache checking?
        # TODO we need some sort of environment
        result = loader.load(env, args)
        ok, err = self.check_load_result_type(result)
        if not ok:
            raise TypeError(err)
        return result

    def check_load_result_type(self, result):
        if not isinstance(result, (tuple, basestring)):
            return False, "Loader must return tuple or basestring"

        # If it is a tuple, make sure it's components are ok.
        if isinstance(result, tuple):
            if not len(result) == 2:
                return False, "Tuple returned from Loader must have two elements"
            name, value = result

            if not isinstance(name, basestring):
                return False, "First element of Tuple returned from Loader must be string"

            if not jinja2.compiler.has_safe_repr(value):
                return False, "Second element of Tuple returned from Loader must have safe repr"
        return True, None
