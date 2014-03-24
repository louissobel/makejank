from . import BaseLoader

SCRIPT_TEMPLATE = """<script type="text/javascript">
%s
</script>"""


class JSLoader(BaseLoader):

    tag = 'js'

    def load(self, env, args):
        filename = args[0]

        try:
            with open(env.resolve_path(filename)) as f:
                script = f.read()
        except IOError:
            # TODO: WHAT DO WE DO
            raise ValueError

        return SCRIPT_TEMPLATE % script