from . import FileLoader, LoaderWrappingLoader

CSS_TEMPLATE = """<style type="text/css">
%s
</style>"""

class CSSLoader(LoaderWrappingLoader):

    tag = 'css'
    WRAPPED_LOADER = FileLoader()
    DIFFERENT_FOR_PRODUCTION = False

    def wrap_result(self, env, arg, kwargs, result):
        return CSS_TEMPLATE % result
