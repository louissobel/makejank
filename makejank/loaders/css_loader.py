from . import BaseLoader

CSS_TEMPLATE = """<style type="text/css">
%s
</style>"""

class CSSLoader(BaseLoader):

    tag = 'css'

    def product(self, env, filename, kwargs):
        return None

    def dependencies(self, env, filename, kwargs):
        return set([env.resolve_path(filename)])

    def load(self, env, filename, kwargs):
        pathname = env.resolve_path(filename)
        try:
            with open(pathname) as f:
                css = f.read()
        except IOError as e:
            raise ValueError("Error reading file %s: %s" % (pathname, e.strerror))

        return CSS_TEMPLATE % css