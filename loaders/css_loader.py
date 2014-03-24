from . import BaseLoader

CSS_TEMPLATE = """<style type="text/css">
%s
</style>"""

class CSSLoader(BaseLoader):

    tag = 'css'

    def load(self, env, args):
        filename = args[0]

        try:
            with open(env.resolve_path(filename)) as f:
                css = f.read()
        except IOError:
            # TODO: WHAT DO WE DO
            raise ValueError

        return CSS_TEMPLATE % css