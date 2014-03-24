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

        # TODO: the way we mutate this is _NOT_ threadsafe OR reentrant
        #       maybe only allow task per renderer? blerg recursion
        #       maybe dep seeking belongs somewehre else entirely?
        #       hmmmm
        self.jinja_env.makejank_load_callback = None

        self.loader_manager = loader_manager
        self.env = environment.Environment(rootpath)

    def do_load(self, load_type, args):
        """
        Callback called by Load node while it is being parsed
         - calls out to LoaderManager to get a result
        """
        try:
            res = self.loader_manager.service(self.env, load_type, args)
        except KeyError:
            raise ValueError("Unable to find loader argument %s" % load_type)
        except TypeError:
            # TODO: do we need some kind of standard interface for jinja errors?
            # this is a misbehaving loader
            raise

        if isinstance(res, basestring):
            return jinja2.nodes.Output([jinja2.nodes.Const(res)])
        elif isinstance(res, tuple):
            name, value = res
            # LoaderManager takes care of type checking for us.
            return jinja2.nodes.Assign(
                jinja2.nodes.Name(name, 'store'),
                jinja2.nodes.Const(value),
            )
        else:
            raise AssertionError("LoaderManager must disallow this!")

    def _track_deps(self, deps, load_type, args):
        """
        mutates list set deps by adding to it from loader_manager queries
        """
        try:
            deps |= set(self.loader_manager.get_deps(self.env, load_type, args))
        except KeyError:
            raise ValueError("Unable to find loader with type %s" % load_type)
        except ValueError:
            # misbehaving loader. what do we do?
            # TODO what do we do?
            raise

    def get_deps(self, template_file):
        source, filename, _ = self.jinja_loader.get_source(
            self.jinja_env,
            template_file,
        )
        deps = set()
        self.jinja_env.makejank_load_callback = lambda lt, a : self._track_deps(deps, lt, a)
        self.jinja_env.parse(source)
        self.jinja_env.makejank_load_callback = None
        return deps

    def render(self, template_file):
        # TODO we also want to be able to render from a strign
        # TODO we also want to be able to pass in data?
        self.jinja_env.makejank_load_callback = self.do_load
        tem = self.jinja_env.get_template(template_file)
        r = tem.render()
        self.jinja_env.makejank_load_callback = None
        return r