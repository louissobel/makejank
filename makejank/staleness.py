"""
exposes a function for determining if something is stale
"""
import os.path
import os

def _mtime(path):
    """
    returns int mtime of path
    raises OSError

    a little duplicated with the logic in FilesystemCache, but im ok with that
    sufficiently different and small
    """
    st = os.stat(path)
    return int(st.st_mtime)

def is_stale(last_modified, deps):
    """
    last_modified - intger, epoch time in seconds since something
                            was last modified
    deps - list of absolute file paths (strings)

    pretty basic:
        find mtime of all deps. if any is greater than last_modified,
        return True, otherwise False

    edge case: if any of the deps cannot be found, returns True (TODO ok?)
    edge case: if no deps are given, always returns False
    edge case: if last_modified is None, return True

    if any of the paths aren't absolute, raises a type error (startswith(/))
    """
    if last_modified is None:
        return True

    for dep in deps:
        if not os.path.isabs(dep):
            raise TypeError("Deps to is_stale must be absolute: %s" % dep)

    try:
        mtimes = [_mtime(dep) for dep in deps]
    except OSError:
        # Assume this means the path does not exist.
        return True

    # use >= to be _sure_, because we're dealing with seconds.
    return any(mtime >= last_modified for mtime in mtimes)
    