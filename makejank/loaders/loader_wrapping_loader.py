"""
Abstract loader that loads another loader
then filters the result somehow
"""

from . import BaseLoader

class LoaderWrappingLoader(BaseLoader):

    WRAPPED_LOADER = None

    def product(self, env, arg, kwargs):
        if self.should_wrap(env, arg, kwargs):
            # We are going to wrap, so our product
            # should be different, use the normal BaseLoaderWrapper
            return BaseLoader.product(self, env, arg, kwargs)
        else:
            # Transparently proxy to the wrapped loader
            return self.WRAPPED_LOADER.product(env, arg, kwargs)

    def dependencies(self, env, arg, kwargs):
        return env.loader_manager.access_loader(
            env,
            self.WRAPPED_LOADER,
            arg,
            kwargs,
            get_deps=True,
        )

    def load(self, env, arg, kwargs):
        result = env.loader_manager.access_loader(
            env,
            self.WRAPPED_LOADER,
            arg,
            kwargs,
        )
        if self.should_wrap(env, arg, kwargs):
            return self.wrap_result(env, arg, kwargs, result)
        else:
            return result

    def should_wrap(self, env, arg, kwargs):
        """
        Override this to control when wrapping should not happen
        """
        return True

    def wrap_result(self, env, arg, kwargs, result):
        raise NotImplementedError
    