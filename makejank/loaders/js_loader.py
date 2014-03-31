from . import BaseLoader

SCRIPT_TEMPLATE = """<script type="text/javascript">
%s
</script>"""


class JSLoader(BaseLoader):

    tag = 'js'

    def dependency_graph(self, env, args):
        filename = args[0]
        return None, set([env.resolve_path(filename)])

    def load(self, env, args):
        filename = args[0]

        pathname = env.resolve_path(filename)
        try:
            with open(pathname) as f:
                script = f.read()
        except IOError as e:
            raise ValueError("Error reading file %s: %s" % (pathname, e.strerror))

        return SCRIPT_TEMPLATE % script