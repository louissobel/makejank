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

        args = []
        while parser.stream.current.type != 'block_end':
            args.append(parser.parse_expression())

        # check that args is either Const or Name
        s_args = []
        for arg in args:
            if isinstance(arg, jinja2.nodes.Const):
                s_args.append(arg.value)
            elif isinstance(arg, jinja2.nodes.Name):
                s_args.append(arg.name)
            else:
                raise jinja2.TemplateSyntaxError(
                    "Arguments to load must be strings or bare keywords. Got %s" % type(arg).__name__,
                    lineno,
                    parser.name,
                    parser.filename,
                )

        node = self.environment.makejank_load_callback(load_type, s_args)
        return node
