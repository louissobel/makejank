"""
Cache interface

 - get(key)
 - last_modified(key) --> None (if not exists) or last modified in unix
 - put (key, value)
"""
import os.path

class _CacheAccessException(IOError):
    """
    Internal Exception
    """
    pass

class FilesystemCache(object):
    """
    Because a cache is allowed to drop keys,
    if there are IOError or OSError,
    it as just as if the key is disapperaed,
    or we wrote it to a black hole
    """
    def __init__(self, cachedir):
        """
        performs a check to see if we can write / read to / from this directory
        """
        self.cachedir = cachedir
        # self._check_write_read(cachedir)

    def last_modified(self, key):
        try:
            times = self._filetimes(key)
        except _CacheAccessException:
            return None
        else:
            # TODO: do we need to look at created time too?
            return times['modified']

    def get(self, key):
        try:
            value = self._read_file(key)
        except _CacheAccessException:
            return None
        else:
            return value

    def put(self, key, value):
        try:
            self._write_file(key, value)
        except _CacheAccessException:
            # FINE (TODO: what does put return)
            pass

    def _write_file(self, filename, contents):
        path = self._get_path(filename)
        try:
            with open(path, 'wb') as f:
                f.seek(0)
                f.write(contents)
                f.truncate()
        except IOError:
            raise _CacheAccessException("Write on %s" % path)

    def _read_file(self, filename):
        path = self._get_path(filename)
        try:
            with open(path, 'rb') as f:
                f.seek(0)
                contents = f.read()
        except IOError:
            raise _CacheAccessException("Read on %s" % path)
        else:
            return contents

    def _filetimes(self, filename):
        """
        returns accessed, created, modified dictionary from stat call
        """
        path = self._get_path(filename)
        try:
            st = os.stat(path)
        except OSError:
            raise _CacheAccessException("Stat on %s" % path)
        else:
            return {
                'accessed': int(st.st_atime),
                'created': int(st.st_ctime),
                'modified': int(st.st_mtime),
            }

    def _get_path(self, filename):
        return os.path.join(self.cachedir, filename)
