import sys
import os
import os.path

import environment
from loaders import *
from caches import FilesystemCache

env = environment.Environment(
    rootdir=os.getcwd(),
    loaders=[
        YamlLoader(),
        CSSLoader(),
        JSLoader(),
        ImgLoader(),
    ],
    cache=FilesystemCache('.makejank_cache')
)

print env.get_deps('test/data/example/page.html')
print env.render('test/data/example/page.html')
