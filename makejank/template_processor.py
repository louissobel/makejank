"""
Abstract Template Processor
Subclasses must specify a load_callback
which is called with (load_type, args)
Sets up a jinja_environment and shit
"""

"""
Wraps Jinja2 to render a makejank template
"""
import jinja2

import jinja_extensions
import environment

class TemplateProcessor(object):

    def __init__(self, env):
        self.jinja_loader = jinja2.FileSystemLoader(['/', env.rootdir])
        self.jinja_env = jinja2.Environment(
            loader=self.jinja_loader,
            extensions=[jinja_extensions.LoadExtension],
        )

        self.jinja_env.makejank_load_callback = self.load_callback
        self.env = env

    def load_callback(self, load_type, arg, kwargs):
        raise NotImplementedError

    def get_source(self, template_filename):
        source, _, _ = self.jinja_loader.get_source(
            self.jinja_env,
            template_filename,
        )
        return source

    def get_source_and_process(self, template_filename):
        source = self.get_source(template_filename)
        return self.process(source)

    def process(self, source):
        raise NotImplementedError