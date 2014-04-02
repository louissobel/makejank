from . import FileLoader

CSS_TEMPLATE = """<style type="text/css">
%s
</style>"""

class CSSLoader(FileLoader):

    tag = 'css'

    def process_file_contents(self, contents, env, filename, kwargs):
        return CSS_TEMPLATE % contents
