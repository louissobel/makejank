import os.path

import jinja2
from jinja2.ext import Extension

class LoadExtension(Extension):
    """
    Extension that creates tag 'load' tag

    Example:
        {% load "lib/stdlib.pbi" %}

    The first part of the basename is the files identifer - this case would be 'stdlib'

    A file is only ever _included_ once (it's text is outputted only once)
    A file is _imported_ to its identifer every time load is called

    So after this statement, macros and variables defined in stdlib.pbi could be accessed
    stdlib.my_macro
    stdlib.my_variable

    etc.
    """

    _TAG_NAME = 'load'

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
        load_type = parser.parse_expression()
        if not isinstance(load_type, jinja2.nodes.Name):
            raise jinja2.TemplateSyntaxError(
                "Argument after 'load' must be bare keyword. Got %s" % type(load_type).__name__,
                lineno,
                parser.name,
                parser.filename,
            )
        load_type = load_type.name

        # First arg is simple expression, and is optional.
        if parser.stream.current.type == 'block_end':
            first_arg_node = None
        else:
            first_arg_node = parser.parse_expression()

        kwargs_list = []
        while parser.stream.current.type != 'block_end':
            if kwargs_list:
                parser.stream.expect('comma')
            target = parser.parse_assign_target(name_only=True)
            parser.stream.expect('assign')
            expression = parser.parse_expression()
            kwargs_list.append((target, expression))

        if first_arg_node is None:
            first_arg = None
        else:
            first_arg = self._get_value_or_raise(first_arg_node, lineno, parser)

        kwargs = {}
        for k_node, v_node in kwargs_list:
            # kNode will be a Name, asserted by name_only option when parsed.
            k = k_node.name
            v = self._get_value_or_raise(v_node, lineno, parser)
            kwargs[k] = v

        try:
            node = self.environment.makejank_load_callback(load_type, first_arg, kwargs)
        except (TypeError, ValueError) as e:
            raise jinja2.TemplateAssertionError(e.message, lineno, parser.name, parser.filename)
        except SyntaxError as e:
            raise jinja2.TemplateSyntaxError(e.message, lineno, parser.name, parser.filename)
        # Let other exceptions bubble up.
        return node

    def _get_value_or_raise(self, node, lineno, parser):
        """
        Asserts that node is either a Const or Name
        """
        if isinstance(node, jinja2.nodes.Const):
            return node.value
        elif isinstance(node, jinja2.nodes.Name):
            return node.name
        else:
            raise jinja2.TemplateSyntaxError(
                "Arguments to load must be strings or bare keywords. Got %s" % type(node).__name__,
                lineno,
                parser.name,
                parser.filename,
            )
