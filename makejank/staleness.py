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

def is_stale(product_last_modified, deps):
    """
    product_last_modified - intger, epoch time in seconds the product
                            was last modified
    deps - list of absolute file paths (strings)

    pretty basic:
        find mtime of all deps. if any is greater than product_last_modified,
        return True, otherwise False

    edge case: if any of the deps cannot be found, returns True (TODO ok?)
    edge case: if no deps are given, always returns False
    edge case: if product_last_modified is None, return True

    if any of the paths aren't absolute, raises a type error (startswith(/))
    """
    if product_last_modified is None:
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
    return any(mtime >= product_last_modified for mtime in mtimes)
    