"""
Manages a set of loaders.
Finding them, and passing data to them
service method takes care of cacheing?
"""
import os.path

import logging
logger = logging.getLogger(__name__)

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

    def get_deps(self, env, loader_tag, arg, kwargs):
        return self._access_loader(env, loader_tag, arg, kwargs, get_deps=True)

    def service(self, env, loader_tag, arg, kwargs):
        return self._access_loader(env, loader_tag, arg, kwargs)

    def _access_loader(self, env, loader_tag, arg, kwargs, get_deps=False):
        logger.debug(
            "Accessing loader %s, arg=%r, kwargs=%r, get_deps=%r",
            loader_tag,
            arg,
            kwargs,
            get_deps,
        )
        loader = self.get_loader(loader_tag) # Raises KeyError

        product = loader.product(env, arg, **kwargs)
        dontcache = product is None or self.cache is None

        if dontcache:
            logger.debug("Skipping cache (product=%r, hascache=%r)", product, self.cache is None)
            if get_deps:
                deps = self._dependencies_and_check(loader, env, arg, kwargs)
                logger.debug("Got deps: %r", deps)
                return deps
            else:
                result = self._load_and_check(loader, env, arg, kwargs)
                logger.debug("Got result: %.40r...", result)
                return result

        # Cache
        deps_cache_key = product + ':dependencies' # TODO TODO TODO collisions :/
        cached_deps = self.cache.get(deps_cache_key)

        # Determine staleness.
        if cached_deps is None:
            # Because there were no cached deps,
            # the product itself must not be cached,
            # so stale is infinitely True.
            logger.debug("No cached deps at %s, %s is stale", deps_cache_key, product)
            stale = True
        else:
            # The product will be stale if any of its dependencies have changed.
            # The product will be fresh if none of its dependencies have changed.
            product_last_modified = self.cache.last_modified(product)
            # is_stale returns True if first arugment is None..
            # so if the product_last_modified is None
            # (the product is not in the cache)
            # stale will be True.
            stale = staleness.is_stale(product_last_modified, cached_deps)
            logger.debug(
                "Checking staleness of product %s (lm: %r) -> stale=%r",
                product,
                product_last_modified,
                stale,
            )

        # so stale means either
        # (deps_cache_key \not\in cache) || (product \not\in cache)
        if stale:
            deps = self._dependencies_and_check(loader, env, arg, kwargs)
            logger.debug("Stale deps, recomputed to: %r", deps)
            self.cache.put(deps_cache_key, deps)
            if get_deps:
                # Then we're done.
                return deps
            result = self._load_and_check(loader, env, arg, kwargs)
            self.cache.put(product, result)
            logger.debug("Stale result, recomputed to: %.40r...", result)
            return result
        else:
            # The cached values do not need to be type checked
            # because they will only be cached if they pass the
            # type checks.
            if get_deps:
                # cached_deps will not be None, becuase if it is,
                # that stale must also be True
                logger.debug("Cached deps are fresh, returning: %r", cached_deps)
                return cached_deps

            result = self.cache.get(product)
            logger.debug("Cached result is fresh, returning: %.40r...", result)
            return result

    def _dependencies_and_check(self, l, env, arg, kwargs):
        ds = l.dependencies(env, arg, **kwargs)
        ok, err = self.check_deps_types(ds)
        if not ok:
            raise TypeError(err)
        return ds

    def _load_and_check(self, l, env, arg, kwargs):
        r = l.load(env, arg, **kwargs)
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
