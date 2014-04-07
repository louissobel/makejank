import sys
import os
import os.path
import logging
import argparse

import yaml

import environment
from loaders import *
from caches import FilesystemCache
from renderer import Renderer
from dependency_detector import DependencyDetector

JANKMODE = 'jank'
SOURCEMODE = 'source'
LOADMODE = 'load'

DEFAULT_JANKFILE_NAME = 'Jankfile'
DEFAULT_CACHE_DIR = '.makejank_cache'
DEFAULT_OUTPUT_DIR = 'jank'

class Makejank(object):

    def __init__(self,
        cache_dir,
        base_dir,
        mode,
        source,
        load,
        output_dir,
        jankfile,
        target,
        deps,
    ):
        cwd = os.getcwd()
        if cache_dir is None:
            cache = None
        else:
            cache = FilesystemCache(cache_dir)

        loaders = [
            YamlLoader(),
            CSSLoader(),
            JSLoader(),
            ImgLoader(),
            MakejankLoader(),
        ]

        rootdir = base_dir

        self.env = environment.Environment(
            rootdir=rootdir,
            loaders=loaders,
            cache=cache,
        )

        if mode == SOURCEMODE:
            source_path = os.path.join(cwd, source)
            if args.deps:
                for dep in self.get_deps('makejank', source_path):
                    print dep
            else:
                print self.render('makejank', source_path)
        elif mode == LOADMODE:
            if args.deps:
                for dep in self.get_deps_load_string(load):
                    print dep
            else:
                print self.render_load_string(load)
        elif mode == JANKMODE:
            # if target is selected, just build that one, otherwise build them all
            print "JANKFILE WITH TARGETS"
            print jankfile['targets']
            print base_dir, cache_dir, output_dir
        else:
            raise AssertionError("Mode none of the modes")


    def render(self, loader_tag, arg, kwargs=None):
        if kwargs is None:
            kwargs = {}
        return self.env.loader_manager.service(self.env, loader_tag, arg, kwargs)

    def get_deps(self, loader_tag, arg, kwargs=None):
        if kwargs is None:
            kwargs = {}
        return self.env.loader_manager.get_deps(self.env, loader_tag, arg, kwargs)

    def render_load_string(self, args):
        """
        as if you had a template {% load args %}
        """
        template = "{% load " + args + " %}"
        # TODO - could handle deps here too, or at least should blow up.
        return Renderer(self.env).process(template)

    def get_deps_load_string(self, args):
        """
        as if you had a template {% load args %}
        """
        template = "{% load " + args + " %}"
        # TODO - could handle deps here too, or at least should blow up.
        return DependencyDetector(self.env).process(template)

def main():
    logging.basicConfig(level=logging.INFO)

    parser = get_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    kwargs = get_kwargs(args, parser)
    Makejank(**kwargs)

def get_parser():

    parser = argparse.ArgumentParser(
        description='Render a makejank template.',
        usage='%(prog)s [source | [-j JANKFILE] -t TARGET | --load STRING] [options]',
    )

    # Three uses - 
    # with a jankfile and without, but whatever. for now no Jankfile.
    source_group = parser.add_argument_group(title="makejank source").add_mutually_exclusive_group()
    source_group.add_argument('source', nargs='?') # TODO
    source_group.add_argument('-j','--jankfile')
    source_group.add_argument('--load')

    # TODO this mutex is a little janky now
    parser.add_argument('-t', '--target') # TODO (jankfile target)

    parser.add_argument(
        '--deps',
        action='store_true',
        default=False,
        help='Print out dependencies, one per line',
    )

    # config options
    config_group = parser.add_argument_group(title="configuration options")
    config_group.add_argument(
        '-b',
        '--base-dir',
        default=None,
        help="Directory off of which relative paths will be resolved"
    )
    config_group.add_argument(
        '--output-dir',
        default=None,
        help="Where do you put built jankfiles? Only useful with Jankfile",
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
        default=None,
        help="Directory for the cache. Absolute or relative to BASE_DIR"
    )

    # Misc.
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        default=False,
        help="Verbose output on stderr",
    )
    return parser

def get_kwargs(args, parser):
    kwargs = {}

    if args.source:
        mode = SOURCEMODE
    elif args.load:
        mode = LOADMODE
    else:
        mode = JANKMODE
    kwargs['mode'] = mode

    # Enforce restrictions
    # - output dir only with jankfile
    # - target only with jankfile
    # - nocache / cachedir handled by argparse
    # - --deps requires SOURCE / JANKMODE or -t

    if args.output_dir and mode != JANKMODE:
        parser.error('Output Dir only can be used with a Jankfile')

    if args.target and not mode == JANKMODE:
        parser.error('-t / --target only can be used with Jankfile')

    if args.deps:
        if mode == JANKMODE and not args.target:
            parser.error('when using a Jankfile can only use --deps with a specified --target')

    # OK, if we're in JANKMODE, try and read a Jankfile
    if mode == JANKMODE:
        jankfile_path = args.jankfile or DEFAULT_JANKFILE_NAME
        # TODO handle error here.
        with open(jankfile_path, 'r') as f:
            jankfile = yaml.load(f.read()) or {} # TODO what if loaded yaml is a list?
    else:
        # Make it empty
        jankfile = {}

    kwargs['jankfile'] = jankfile

    kwargs['target'] = args.target
    kwargs['deps'] = args.deps
    kwargs['source'] = args.source or None
    kwargs['load'] = args.load

    # Determine base dir
    kwargs['base_dir'] = determine_base_dir(kwargs, args)
    kwargs['cache_dir'] = determine_cache_dir(kwargs, args)
    kwargs['output_dir'] = determine_output_dir(kwargs, args)

    return kwargs

def determine_base_dir(kwargs, args):
    cwd = os.getcwd()
    jankfile = kwargs['jankfile']
    mode = kwargs['mode']

    if args.base_dir:
        return os.path.join(cwd, args.base_dir)
    else:
        if mode == JANKMODE:
            jankfile_path = args.jankfile or DEFAULT_JANKFILE_NAME
            jankdir = os.path.dirname(os.path.abspath(jankfile_path))
            # First check jankfile, then directory of jankfile
            if jankfile.get('base_dir'):
                return os.path.join(jankdir, jankfile['base_dir'])
            else:
                # Default to the directory the jankfile is in
                return jankdir
        else:
            # Default to the cwd
            return cwd

def determine_cache_dir(kwargs, args):
    cwd = os.getcwd()
    base_dir = kwargs['base_dir']
    jankfile = kwargs['jankfile']
    mode = kwargs['mode']

    if args.no_cache:
        return None

    if args.cache_dir:
        # if specified on command line, consider
        # relative to where we
        return os.path.join(cwd, args.cache_dir)

    if mode == JANKMODE:
        return os.path.join(base_dir, jankfile.get('cache_dir', DEFAULT_CACHE_DIR))
    else:
        return os.path.join(base_dir, DEFAULT_CACHE_DIR)

def determine_output_dir(kwargs, args):
    cwd = os.getcwd()
    base_dir = kwargs['base_dir']
    jankfile = kwargs['jankfile']
    mode = kwargs['mode']

    if args.output_dir:
        return os.path.join(cwd, args.output_dir)

    else:
        if mode == JANKMODE:
            return os.path.join(base_dir, jankfile.get('output_dir', DEFAULT_OUTPUT_DIR))
        else:
            return None

if __name__ == "__main__":
    main()
