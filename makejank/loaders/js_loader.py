from . import FileLoader

SCRIPT_TEMPLATE = """<script type="text/javascript">
%s
</script>"""


class JSLoader(FileLoader):

    tag = 'js'

    def process_file_contents(self, contents):
        return SCRIPT_TEMPLATE % contents
