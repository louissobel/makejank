import sys
import os
import os.path

import jinja2

from loaders import *
from renderer import Renderer
from loader_manager import LoaderManager

lm = LoaderManager()
lm.register(YamlLoader())
lm.register(CSSLoader())
lm.register(JSLoader())

r = Renderer(os.getcwd(), lm)
print r.render('example/page.html')
