"""
Loader Finder
"""
import os
import sys

MAKEJANK_STDLIB_PACKAGE='makejank.loaders'
LOADER_MODULE_TEMPLATE = "makejank_%s"
LOADER_KLASS_ATTRIBUTE = 'loader'

from .loaders import BaseLoader

class LoaderFinder(object):

    def __init__(self):
        sys.path.append(os.getcwd())

    def find(self, loader_tag, from_package=None):
        """
        finds a loader with the given loader tag

        if from given:
            look in from for `makejank_%s` % loader_tag

        otherwise:
             - first look stdlib (from MAKEJANK_STDLIB_PACKAGE)
             - then try a naked import

        raises ValueError if it cannot find, import, and initialize requested loader
        """
        loader_module_name = self._loader_tag_to_module_name(loader_tag)
        if from_package is not None:
            loader_module = self._import(loader_module_name, from_package)

        else:
            # first look in stdlib
            loader_module = self._import(loader_module_name, MAKEJANK_STDLIB_PACKAGE)
            if loader_module is None:
                loader_module = self._import(loader_module_name)

        if loader_module is None:
            msg = "Unable to find loader %s (module %s%s)" % (
                loader_tag,
                loader_module_name,
                "" if from_package is None else " from %s" % from_package,
            )
            raise ValueError(msg)

        # get the .loader module attribute
        try:
            loader_klass = getattr(loader_module, LOADER_KLASS_ATTRIBUTE)
        except AttributeError:
            raise ValueError("Unable to create loader %s, module %s has no attribute %s" % (
                loader_tag,
                loader_module_name,
                LOADER_KLASS_ATTRIBUTE,
            ))

        # Ok, we have the klass.
        # Try to create it.
        # This should raise a ValueError if it cannot be created,
        # which we allow to bubble up.
        loader = loader_klass()

        # Do a quick type check.
        if not isinstance(loader, BaseLoader):
            raise ValueError("Loader %s is not a BaseLoader!" % loader_tag)

        return loader

    def _loader_tag_to_module_name(self, loader_tag):
        return LOADER_MODULE_TEMPLATE % loader_tag

    def _import(self, module_name, from_package=None):
        try:
            from_list = [] if from_package is None else [module_name]
            search_module = module_name if from_package is None else from_package
            module = __import__(search_module, globals(), locals(), from_list, -1)
        except ImportError:
            return None

        if from_package is not None:
            return getattr(module, module_name, None)
        else:
            return module
