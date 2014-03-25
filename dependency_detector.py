"""
TemplateProcessor that detects dependencies in a makejank
"""

from template_processor import TemplateProcessor

class DependencyDetector(TemplateProcessor):
    """
    Only should have process called once
    TODO: should we enforce that ^^
    or actually, it is just not threadsafe or recursion safe :/
    but we'll detect and blow up (relying on python atomicity)
    """

    def __init__(self, *args, **kwargs):
        TemplateProcessor.__init__(self, *args, **kwargs)
        self._getting_deps = False

    def load_callback(self, load_type, args):
        """
        mutates list set deps by adding to it from loader_manager queries
        """
        try:
            self.deps |= set(self.env.loader_manager.get_deps(
                self.env,
                load_type,
                args,
            ))
        except KeyError:
            raise ValueError("Unable to find loader with type %s" % load_type)
        except ValueError:
            # misbehaving loader. what do we do?
            # TODO what do we do?
            raise

    def process(self, template_filename):
        if self._getting_deps is True:
            raise AssertionError("DependencyDetector is not reentrant. Create a new one")
        self._getting_deps = True

        source, filename, _ = self.jinja_loader.get_source(
            self.jinja_env,
            template_filename,
        )
        self.deps = set()
        self.jinja_env.parse(source)

        self._getting_deps = False
        return self.deps
