import sys
import os
import os.path

import environment
from loaders import *
from caches import FilesystemCache

rootdir = os.path.join(os.getcwd(), 'test/data')
env = environment.Environment(
    rootdir=rootdir,
    loaders=[
        YamlLoader(),
        CSSLoader(),
        JSLoader(),
        ImgLoader(),
    ],
    cache=FilesystemCache('.makejank_cache')
)

#print env.get_deps('example/page.html')
print env.render('example/page.html')
