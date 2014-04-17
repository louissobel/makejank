import os.path

import jinja2
from jinja2.ext import Extension

class UseExtension(Extension):
    """
    Extension that creates tag 'use' tag

    {% use <name:loader_tag> [from <getattr|name:from_package>]}
    Example:
        {% use foo %}
        {% use foo from bar %}
        {% use foo from bar.hehe %}

    Will parse args and call environment.makejank_use_callback
    with args (loader_tag, from_package), with from_package maybe None
    """

    _TAG_NAME = 'use'

    # declare which strings set off this extension
    tags = set([_TAG_NAME])

    def __init__(self, environment):
        Extension.__init__(self, environment)

    def parse(self, parser):
        # the first token is the token that started the tag.
        # get the line number so that we can give
        # that line number to the nodes we create by hand.
        lineno = parser.stream.next().lineno

        # ok, first arg is load type
        loader_tag = parser.parse_expression()
        if not isinstance(loader_tag, jinja2.nodes.Name):
            raise jinja2.TemplateSyntaxError(
                "Loader tag after 'use' must be bare keyword. Got %s" % type(loader_tag).__name__,
                lineno,
                parser.name,
                parser.filename,
            )
        loader_tag = loader_tag.name

        # Optionally have a from.
        if parser.stream.current.type == 'block_end':
            from_package=None
        else:
            from_keyword = parser.parse_expression()
            if not (isinstance(from_keyword, jinja2.nodes.Name) and from_keyword.name == 'from'):
                raise jinja2.TemplateSyntaxError(
                    "Expected `from` keyword in `use` statement. Got %s" % type(from_keyword).__name__,
                    lineno,
                    parser.name,
                    parser.filename,
                )

            if parser.stream.current.type == 'block_end':
                raise jinja2.TemplateSyntaxError(
                    "Missing argument to `from`, expected package name.",
                    lineno,
                    parser.name,
                    parser.filename,
                )

            from_package_node = parser.parse_expression()
            try:
                from_package = self._flatten_getattr_tree(from_package_node)
            except TypeError:
                raise jinja2.TemplateSyntaxError(
                    "Argument to from must be dotted package name!",
                    lineno,
                    parser.name,
                    parser.filename,
                )

        # TODO: error handling
        self.environment.makejank_use_callback(loader_tag, from_package)

    def _flatten_getattr_tree(self, node):
        """
        node is either getattr or name
        if name, returns name
        otherwise, returns _flatten_getattr_tree(node.left) + "." + node.attr
        """
        if isinstance(node, jinja2.nodes.Name):
            return node.name
        elif isinstance(node, jinja2.nodes.Getattr):
            return self._flatten_getattr_tree(node.node) + "." + node.attr
        else:
            raise TypeError
