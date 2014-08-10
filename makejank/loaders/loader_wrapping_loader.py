"""
Abstract loader that loads another loader
then filters the result somehow
"""

from . import BaseLoader

class LoaderWrappingLoader(BaseLoader):

    WRAPPED_LOADER = None

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
        return self.wrap_result(env, arg, kwargs, result)

    def wrap_result(self, env, arg, kwargs, result):
        raise NotImplementedError
    