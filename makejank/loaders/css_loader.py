from . import BaseLoader

CSS_TEMPLATE = """<style type="text/css">
%s
</style>"""

class CSSLoader(BaseLoader):

    tag = 'css'

    def load(self, env, args):
        filename = args[0]
        pathname = env.resolve_path(filename)
        try:
            with open(pathname) as f:
                css = f.read()
        except IOError as e:
            raise ValueError("Error reading file %s: %s" % (pathname, e.strerror))

        return CSS_TEMPLATE % css