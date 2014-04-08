import sys
import os
import os.path
import logging
import argparse
import time

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


def main():
    logging.basicConfig(level=logging.INFO)

    parser = get_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    config = get_config(args, parser)
    env = get_env(config)

    mode = config['mode']
    if mode == SOURCEMODE or mode == LOADMODE:
        get_deps = args.deps
        if mode == SOURCEMODE:
            source_path = os.path.join(cwd, source)
            result = env.render_template(source_path, get_deps=get_deps)
        else:
            result = env.render_load_args(args.load, get_deps=get_deps)

        if args.deps:
            for dep in result:
                print dep
        else:
            print result

    elif mode == JANKMODE:
        # if target is selected, just build that one, otherwise build them all
        # TODO HANDLE A TARGET (multiple?)
        # TODO should we check up-to-dateness of products
        # TODO handle get_deps of that target
        jankfile = config['jankfile']
        output_dir = config['output_dir']
        # TODO create output dir if it does not exist?

        # TODO this should be moved to a function
        targets = jankfile.get('targets')
        if not targets:
            # TODO err log
            print "No targets."
        else:
            for target in targets:
                action = targets[target]
                target_file = os.path.join(output_dir, target)
                # TODO we have to make sure the directories exist all the way down.
                start = time.time()
                print "%s: %s..." % (target_file, action),

                # TODO error handling
                with open(target_file, 'w') as f:
                    f.write(env.render_load_args(action))

                print "ok",
                done = time.time()
                print "(%f)" % (done - start)
    else:
        raise AssertionError("Mode none of the modes")

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

def get_config(args, parser):
    config = {}

    if args.source:
        mode = SOURCEMODE
    elif args.load:
        mode = LOADMODE
    else:
        mode = JANKMODE
    config['mode'] = mode

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

    config['jankfile'] = jankfile

    config['target'] = args.target
    config['deps'] = args.deps
    config['source'] = args.source or None
    config['load'] = args.load

    # Determine base dir
    config['base_dir'] = determine_base_dir(config, args)
    config['cache_dir'] = determine_cache_dir(config, args)
    config['output_dir'] = determine_output_dir(config, args)

    return config

def determine_base_dir(config, args):
    cwd = os.getcwd()
    jankfile = config['jankfile']
    mode = config['mode']

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

def determine_cache_dir(config, args):
    cwd = os.getcwd()
    base_dir = config['base_dir']
    jankfile = config['jankfile']
    mode = config['mode']

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

def determine_output_dir(config, args):
    cwd = os.getcwd()
    base_dir = config['base_dir']
    jankfile = config['jankfile']
    mode = config['mode']

    if args.output_dir:
        return os.path.join(cwd, args.output_dir)

    else:
        if mode == JANKMODE:
            return os.path.join(base_dir, jankfile.get('output_dir', DEFAULT_OUTPUT_DIR))
        else:
            return None

def get_env(config):

    loaders = [
        YamlLoader(),
        CSSLoader(),
        JSLoader(),
        ImgLoader(),
        MakejankLoader(),
    ]
    # TODO additional loaders

    if config['cache_dir'] is None:
        cache = None
    else:
        cache = FilesystemCache(config['cache_dir'])

    return environment.Environment(
        rootdir=config['base_dir'],
        loaders=loaders,
        cache=cache,
    )

if __name__ == "__main__":
    main()
