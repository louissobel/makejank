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

    def load_callback(self, load_type, args):
        raise NotImplementedError

    def process(self, template_filename):
        # TODO we also want to be able to render from a strign
        # TODO we also want to be able to pass in data?
        raise NotImplementedError