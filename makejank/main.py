import sys
import os
import os.path

import environment
from loaders import *
from caches import FilesystemCache

class Makejank(object):

    def __init__(self, kwargs):
        if kwargs['cache_dir'] is None:
            cache = None
        else:
            cache = FilesystemCache(kwargs['cache_dir'])

        loaders = [
            YamlLoader(),
            CSSLoader(),
            JSLoader(),
            ImgLoader(),
        ]

        rootdir = kwargs['base_dir']

        self.env = environment.Environment(
            rootdir=rootdir,
            loaders=loaders,
            cache=cache,
        )


    def render(self, source_file):
        return self.env.render(source_file)

    def get_deps(self, source_file):
        return self.env.get_deps(source_file)

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Render a makejank template.',
        usage='%(prog)s [source | -t TARGET] [options]',
    )

    # Two uses - 
    # with a jankfile and without, but whatever. for now no Jankfile.
    source_group = parser.add_argument_group(title="makejank source").add_mutually_exclusive_group(required=True)
    source_group.add_argument('source', nargs='?') # TODO
    source_group.add_argument('-t', '--target') # TODO (jankfile target)


    # config options
    config_group = parser.add_argument_group(title="configuration options")
    config_group.add_argument(
        '-b',
        '--base-dir',
        default=None,
        help="Directory off of which relative paths will be resolved"
    )

    cache_group = config_group.add_mutually_exclusive_group()
    cache_group.add_argument(
        '--no-cache',
        action='store_true',
        default=False,
        help="Prevents a cache from being used",
    )
    cache_group.add_argument(
        '-c',
        '--cache-dir',
        default=".makejank_cache",
        help="Directory for the cache. Absolute or relative to BASE_DIR"
    )

    args = parser.parse_args()

    base_dir = os.path.join(os.getcwd(), args.base_dir) if args.base_dir else os.getcwd()
    cache_dir = None if args.no_cache else os.path.join(base_dir, args.cache_dir)

    kwargs = {
        'base_dir': base_dir,
        'cache_dir' : cache_dir,
    }

    makejank = Makejank(kwargs)
    source_path = os.path.join(os.getcwd(), args.source)
    print makejank.render(source_path)

if __name__ == "__main__":
    main()