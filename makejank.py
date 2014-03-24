import sys
import os
import os.path

import jinja2

from loaders import *
from renderer import Renderer
from loader_manager import LoaderManager
from caches import FilesystemCache

cache = FilesystemCache('.makejank_cache')
lm = LoaderManager(cache)
lm.register(YamlLoader())
lm.register(CSSLoader())
lm.register(JSLoader())
lm.register(ImgLoader())

r = Renderer(os.getcwd(), lm)
print r.get_deps('example/page.html')
