"""
Browserify Loader

 - minifies if env.production is set
 - yippee
"""
import subprocess

import slimit

from makejank import BaseLoader, LoaderWrappingLoader

NO_BROWSERIFY_MESSAGE = """
browserify must be installed to use the browserify js loader.
http://browserify.org/#install
"""

class _InnerBrowserifyLoader(BaseLoader):
    """
    Does dependency calculation and computation
    """
    tag = '_browserify_inner'
    DIFFERENT_FOR_PRODUCTION = False

    def __init__(self):
        """
        Make sure that browserify exists
        """
        args = [
            "browserify",
            "--version",
        ]
        try:
            subprocess.check_output(args, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            raise ValueError(NO_BROWSERIFY_MESSAGE)

    def dependencies(self, env, filename, kwargs):
        args = [
            "browserify",
            env.resolve_path(filename),
            '--list',
        ]
        env.logger.debug(' '.join(args))
        try:
            deps_string = subprocess.check_output(args, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            for line in e.output.split('\n'):
                env.logger.error(line)
            raise ValueError('Error getting dependencies')

        dep_lines = deps_string.split('\n')
        return set(filter(None, dep_lines))

    def load(self, env, filename, kwargs):
        args = [
            "browserify",
            env.resolve_path(filename),
        ]
        standalone = kwargs.get('standalone')
        if standalone:
            args.extend([
                '--standalone',
                standalone,
            ])

        env.logger.debug(' '.join(args))
        try:
            javascript = subprocess.check_output(args, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            for line in e.output.split('\n'):
                env.logger.error(line)
            raise ValueError("Error while loading")
        return javascript

SCRIPT_TEMPLATE = "<script type='text/javascript'>%s</script>"

class BrowserifyLoader(LoaderWrappingLoader):

    WRAPPED_LOADER = _InnerBrowserifyLoader()
    tag = 'js'

    def wrap_result(self, env, filename, kwargs, javascript):
        if env.production:
            javascript = slimit.minify(javascript)
        return SCRIPT_TEMPLATE % javascript

loader = BrowserifyLoader
