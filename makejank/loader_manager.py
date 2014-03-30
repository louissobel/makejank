"""
Manages a set of loaders.
Finding them, and passing data to them
service method takes care of cacheing?
"""
import os.path
import cPickle as pickle

import jinja2

import staleness

class LoaderManager(object):

    def __init__(self, cache=None):
        # TODO: should we warn if cache is None?
        self.cache = cache
        self.loaders = {}

    def register(self, loader):
        self.loaders[loader.tag] = loader

    def get_loader(self, loader_tag):
        loader = self.loaders.get(loader_tag)
        if loader is None:
            raise KeyError("Cannot find loader with tag %s" % loader_tag)
        else:
            return loader

    def get_deps(self, env, loader_tag, args):
        loader = self.get_loader(loader_tag) # Raises KeyError

        product, deps = loader.dependency_graph(env, args)
        # Check deps
        ok, err = self.check_deps_types(deps)
        if not ok:
            raise TypeError(err)
        return deps

    def service(self, env, loader_tag, args):
        loader = self.get_loader(loader_tag) # Raises KeyError.

        product, deps = loader.dependency_graph(env, args)
        # Check that deps are all absolute.
        ok, err = self.check_deps_types(deps)
        if not ok:
            raise TypeError(err)

        # TODO: dont cache is signaled with product being None :/
        #       or if we dont have a cache! is that right?
        dontcache = product is None or self.cache is None

        if not dontcache:
            # get last modified of product
            product_last_modified = self.cache.last_modified(product)
            stale = staleness.is_stale(product_last_modified, deps)

        if dontcache:
            result = self._load_and_check(loader, env, args)
        else:
            if stale:
                result = self._load_and_check(loader, env, args)

                self.cache.put(product, pickle.dumps(result))
            else:
                # I don't need to type check here, because it only got
                # _into_ the cache if it has the right type.
                result = pickle.loads(self.cache.get(product))

        return result

    def _load_and_check(self, l, *args):
        r = l.load(*args)
        ok, err = self.check_load_result_type(r)
        if not ok:
            raise TypeError(err)
        return r

    def check_deps_types(self, deps):
        if not isinstance(deps, set):
            return False, "Deps must be a Set"

        for dep in deps:
            if not os.path.isabs(dep):
                return False, "Each dependency in list returned by load must be absolute"
        return True, None

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
