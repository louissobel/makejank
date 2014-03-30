"""
TemplateProcessor that detects dependencies in a makejank
"""
import jinja2

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
            self.deps |= self.env.loader_manager.get_deps(
                self.env,
                load_type,
                args,
            )
        except KeyError:
            raise TypeError("Unable to find loader with type %s" % load_type)
        except TypeError as e:
            # This is a misbehaving loader, re-raise.
            raise
        except ValueError as e:
            # A loader had a problem, re-raise.
            raise
        except SyntaxError as e:
            # Sent up by a loader, re-raise.
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
        tree = self.jinja_env.parse(source)

        # That took care of Loads because of the callback
        # (it's too bad we can't create our own nodes...)
        # Now we walk for includes, imports, extendss
        visitor = DependencyVisitor()
        visitor.visit(tree)
        # visitor.deps can have relative paths.
        # lets make them absolute
        jinja_deps = set(self.env.resolve_path(d) for d in visitor.deps)
        self.deps |= jinja_deps

        # now I need to recurse... (on relative paths)
        # TODO: now we introduce infinite recursion...
        for dep in visitor.deps:
            self.deps |= self.env.get_deps(dep)

        self._getting_deps = False
        return self.deps


class DependencyVisitor(jinja2.visitor.NodeVisitor):

    def __init__(self, *args, **kwargs):
        jinja2.visitor.NodeVisitor.__init__(self, *args, **kwargs)
        self.deps = set()

    def _extract_dep(self, node):
        template = node.template
        if isinstance(template, jinja2.nodes.Name):
            # TODO: this needs to be a warning
            raise ValueError("Can only track string jinja deps")
        if not isinstance(template, jinja2.nodes.Const):
            raise ValueError("Template in dep must be string...")

        self.deps.add(template.value)

    visit_Extends = _extract_dep
    visit_Include = _extract_dep
    visit_Import = _extract_dep
    visit_FromImport = _extract_dep
