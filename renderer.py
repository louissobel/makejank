"""
Wraps Jinja2 to render a makejank template
"""
import jinja2

import jinja_extensions
import environment

class Renderer(object):

    def __init__(self, rootpath, loader_manager):
        self.rootpath = rootpath
        self.jinja_loader = jinja2.FileSystemLoader([rootpath])
        self.jinja_env = jinja2.Environment(loader=self.jinja_loader, extensions=[jinja_extensions.LoadExtension])
        self.jinja_env.makejank_load = self.makejank_load

        self.loader_manager = loader_manager
        self.env = environment.Environment(rootpath)

    def makejank_load(self, load_type, args):
        """
        Callback called by Load node while it is being parsed
         - calls out to LoaderManager to get a result
        """
        # TODO ERROR CHECKING HERE??
        res = self.loader_manager.service(self.env, load_type, args)
        if isinstance(res, basestring):
            return jinja2.nodes.Const(res)
        elif isinstance(res, tuple):
            name, value = res
            # TODO: value must be a "safe" (jinja2 term) value
            #       what happens if it is not?
            return jinja2.nodes.Assign(
                jinja2.nodes.Name(name, 'store'),
                jinja2.nodes.Const(value),
            )
        else:
            # TODO: better error
            raise TypeError

    def render(self, template_file):
        # TODO we also want to be able to render from a strign
        # TODO we also want to be able to pass in data?
        tem = self.jinja_env.get_template(template_file)
        return tem.render()
    