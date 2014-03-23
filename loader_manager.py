"""
Manages a set of loaders.
Finding them, and passing data to them
service method takes care of cacheing?
"""
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
        return loader.load(env, args)
    