"""
logic for actually processing a jankfile
"""
import os
import os.path
import time

import logging
logger = logging.getLogger(__name__)

def process_jankfile(env, jankfile, output_dir):
    """
    process a whole jankfile
    TODO: what should it return?
    """
    targets = jankfile.get('targets')
    if not targets:
        # TODO error log?
        logger.info("No targets.")
    else:
        for target in targets:
            action = targets[target]
            target_file = os.path.join(output_dir, target)

            # TODO we have to make sure the directories exist all the way down.
            # TODO if a target has an absolute path, it needs to be relative
            start = time.time()

            # TODO error handling
            with open(target_file, 'w') as f:
                f.write(env.render_load_args(action))

            # Logging
            done = time.time()
            millis = (done - start) * 1000
            output_target = os.path.relpath(target_file, env.cwd)
            logger.info("%s: %s OK (%.2fms)", output_target, action, millis)

def process_jankfile_target(env, jankfile, target, output_dir):
    """
    process a single target of a jankfile
    """
    pass
