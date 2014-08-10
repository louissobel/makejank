from . import FileLoader, LoaderWrappingLoader

SCRIPT_TEMPLATE = """<script type="text/javascript">
%s
</script>"""


class JSLoader(LoaderWrappingLoader):

    tag = 'js'
    WRAPPED_LOADER = FileLoader()

    def wrap_result(self, env, arg, kwargs, result):
        return SCRIPT_TEMPLATE % result
