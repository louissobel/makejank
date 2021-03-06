"""
TemplateProcessor to render a makejank template
"""
import jinja2

from template_processor import TemplateProcessor

class Renderer(TemplateProcessor):

    def load_callback(self, load_type, arg, kwargs):
        """
        Callback called by Load node while it is being parsed
         - calls out to LoaderManager to get a result
        """
        try:
            res = self.env.loader_manager.service(self.env, load_type, arg, kwargs)
        except KeyError:
            raise TypeError("Unable to find loader of type %s" % load_type)
        except TypeError as e:
            # This is a misbehaving loader, re-raise.
            raise
        except ValueError as e:
            # A loader had a problem, re-raise.
            raise
        except SyntaxError as e:
            # Sent up by a loader, re-raise.
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

    def process(self, source):
        t = self.jinja_env.from_string(source)
        return t.render()
