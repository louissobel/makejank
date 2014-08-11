"""
Manages a set of loaders.
Finding them, and passing data to them
service method takes care of cacheing?
"""
import os.path
import time
import functools

import logging
logger = logging.getLogger(__name__)

import jinja2

import staleness

def time_and_log_access(f):
    @functools.wraps(f)
    def inner(self, env, loader, arg, kwargs, get_deps=False):
        start = time.time() * 1000
        r = f(self, env, loader, arg, kwargs, get_deps)
        done = time.time() * 1000

        action = 'Got dependencies' if get_deps else 'Loaded'
        millis = done - start
        logger.info(" > %s: %s %s %r OK (%.2fms)", action, loader.tag, arg, kwargs, millis)
        return r
    return inner

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
        loader = self.get_loader(loader_tag) # Raises KeyError
        return self.access_loader(env, loader, arg, kwargs, get_deps=True)

    def service(self, env, loader_tag, arg, kwargs):
        loader = self.get_loader(loader_tag) # Raises KeyError
        return self.access_loader(env, loader, arg, kwargs)

    @time_and_log_access
    def access_loader(self, env, loader, arg, kwargs, get_deps=False):
        logger.debug(
            "Accessing loader %s, arg=%r, kwargs=%r, get_deps=%r",
            loader.tag,
            arg,
            kwargs,
            get_deps,
        )
        product_cache_key = loader.product(env, arg, kwargs)
        dontcache = product_cache_key is None or self.cache is None

        if dontcache:
            logger.debug("Skipping cache (product=%r, hascache=%r)", product_cache_key, self.cache is None)
            if get_deps:
                deps = self._dependencies_and_check(loader, env, arg, kwargs)
                logger.debug("Got deps: %r", deps)
                return deps
            else:
                result = self._load_and_check(loader, env, arg, kwargs)
                logger.debug("Got result: %.40r...", result)
                return result

        # Cache
        deps_cache_key = loader.dependencies_product(env, arg, kwargs)
        assert deps_cache_key is not None

        cached_deps = self.cache.get(deps_cache_key)
        # Determine staleness.
        # Dependencies are stale if we dont have them or if any have changed.
        # Product is stale if:
        # - we don't have it
        # - dependencies are stale
        # - dependency last_modified is after product last_modified
        # SO, if dependencies are stale, and we are re-getting them,
        # INVALIDATE the cached product
        if cached_deps is None:
            logger.debug("No cached deps at %s", deps_cache_key)
            stale_deps = True
        else:
            deps_last_modified = self.cache.last_modified(deps_cache_key)
            stale_deps = staleness.is_stale(deps_last_modified, cached_deps)
            logger.debug(
                "Checking staleness of product deps %s (lm: %r) -> stale=%r",
                product_cache_key,
                deps_last_modified,
                stale_deps,
            )

        deps = cached_deps
        if stale_deps:
            deps = self._dependencies_and_check(loader, env, arg, kwargs)
            logger.debug("Stale deps, purging product, recomputed to: %r", deps)
            self.cache.put(deps_cache_key, deps)
            self.cache.put(product_cache_key, None)
        else:
            logger.debug("Cached deps are fresh: %r", deps)

        if get_deps:
            # Then we're done.
            return deps

        cached_product = self.cache.get(product_cache_key)
        product = cached_product
        # Because when getting dependencies we purge if they
        # need updating, the presence of the cached product
        # is enough to know that it is not stale
        if cached_product is None:
            product = self._load_and_check(loader, env, arg, kwargs)
            logger.debug("Stale result, recomputed to: %.40r...", product)
            self.cache.put(product_cache_key, product)
        else:
            logger.debug("Cached result is fresh, returning: %.40r...", product)

        return product

    def _dependencies_and_check(self, l, env, arg, kwargs):
        ds = l.dependencies(env, arg, kwargs)
        ok, err = self.check_deps_types(ds)
        if not ok:
            raise TypeError(err)
        return ds

    def _load_and_check(self, l, env, arg, kwargs):
        r = l.load(env, arg, kwargs)
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
