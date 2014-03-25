import sys
import os
import os.path

import jinja2

import environment
from loaders import *
from loader_manager import LoaderManager
from caches import FilesystemCache

cache = FilesystemCache('.makejank_cache')
lm = LoaderManager(cache)
lm.register(YamlLoader())
lm.register(CSSLoader())
lm.register(JSLoader())
lm.register(ImgLoader())

env = environment.Environment(
    rootdir=os.getcwd(),
    loader_manager=lm,
)

print env.get_deps('example/page.html')
print env.render('example/page.html')
