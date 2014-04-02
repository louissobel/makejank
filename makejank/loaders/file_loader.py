"""
File Loader

For subclassing, calls out to a process_file_contents method
"""

from . import BaseLoader

class FileLoader(BaseLoader):

    tag = 'file'

    def dependencies(self, env, filename, kwargs):
        return set([env.resolve_path(filename)])

    def load(self, env, filename, kwargs):
        pathname = env.resolve_path(filename)
        try:
            with open(pathname) as f:
                contents = f.read()
        except IOError as e:
            raise ValueError("Error reading file %s: %s" % (pathname, e.strerror))

        return self.process_file_contents(contents)

    def process_file_contents(self, contents):
        return contents