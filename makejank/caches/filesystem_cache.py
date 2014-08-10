"""
Cache interface

 - get(key)
 - last_modified(key) --> None (if not exists) or last modified in unix
 - put (key, value)

"""
import os.path
import hashlib
import cPickle as pickle
import shutil
import time

import logging
logger = logging.getLogger(__name__)

class _CacheAccessException(IOError):
    """
    Internal Exception
    """
    pass

class _CacheSerializationError(ValueError):
    """
    InternalException
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
        if not os.path.isabs(cachedir):
            raise ValueError("Must initialize FilesystemCache with an absolute path")

        if not os.path.isdir(cachedir):
            if os.path.exists(cachedir):
                raise ValueError("Cachedir already exists and is not a directory")
            else:
                self._create_cachedir(cachedir)
        self.cachedir = cachedir

        can_read_and_write = self._check_can_read_and_write()
        if not can_read_and_write:
            raise ValueError("Unable to write and read from cachedir")

    def last_modified(self, key):
        start = time.time()
        times, which = self._try_access(self._filetimes, key)
        if which is None:
            result = None
        else:
            result = times['modified']

        duration = time.time() - start
        logger.debug("LAST_MODIFIED (%.2fms) %s -> %s", duration, key, str(result))
        return result

    def get(self, key):
        start = time.time()
        value, which = self._try_access(self._read_file, key)
        if which is None:
            result = None
        elif which == 'string':
            result = value
        elif which == 'object':
            try:
                value = self._deserialize_object(value)
            except _CacheSerializationError:
                logger.warn("GET silently failing deserializing %s" % key)
                result = None
            else:
                result = value
        else:
            raise AssertionError("bad type returned by _try_access")

        duration = time.time() - start
        logger.debug("GET (%.2fms) %s -> %.40r", duration, key, result)
        return result

    def put(self, key, value):
        start = time.time()
        filename = self._hash(key)
        if not isinstance(value, basestring):
            filename = self._object_filename(filename)
            try:
                value = self._serialize_object(value)
            except _CacheSerializationError:
                logger.warn("PUT silently failing serializing %s: %.40r", key, value)
                return

        # Now write out.
        try:
            self._write_file(filename, value)
        except _CacheAccessException:
            logger.warn("PUT silently failing writing %s (%s: %.40r)", filename, key, value)
            return

        duration = time.time() - start
        logger.debug("PUT (%.2fms) %s %.40r", duration, key, value)

    def flush(self):
        self._delete_cachedir(self.cachedir)
        self._create_cachedir(self.cachedir)

    def _try_access(self, method, key):
        filename = self._hash(key)
        # Try to run method on string version.
        try:
            result = method(filename)
        except _CacheAccessException:
            # Try to get the object version.
            try:
                result = method(self._object_filename(filename))
            except _CacheAccessException:
                # Give up. TODO: warn?
                return None, None
            else:
                return result, 'object'
        else:
            return result, 'string'

    def _create_cachedir(self, cachedir):
        try:
            os.mkdir(cachedir)
        except OSError as e:
            # Either some component also doesn't exist
            # or we lack permission. Whatever.
            raise ValueError("Unable to create cachedir: %s" % str(e))

    def _delete_cachedir(self, cachedir):
        """
        Raises ValueError if we can't :/
        """
        try:
            shutil.rmtree(cachedir)
        except OSError as e:
            raise ValueError("Cannot delete cachedir")

    def _check_can_read_and_write(self):
        """
        writes a key, makes sure we get it back,
        the deletes it. a lil jank, because
        we use public and private methods.
        """
        key = 'CHECK_CAN_READ_AND_WRITE'
        value = 'ABC123xyz!@#$'
        self.put(key, value)
        r = self.get(key)
        if not r == value:
            return False

        # Now delete it.
        path = self._get_path(self._hash(key))
        try:
            os.unlink(path)
        except OSError as e:
            return False # This could use some more information.

        return True

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

    def _serialize_object(self, o):
        try:
            return pickle.dumps(o)
        except pickle.PickleError:
            raise _CacheSerializationError

    def _deserialize_object(self, s):
        try:
            return pickle.loads(s)
        except pickle.PickleError:
            raise _CacheSerializationError

    def _object_filename(self, filename):
        return filename + '.object'

    def _hash(self, key):
        m = hashlib.md5()
        m.update(key)
        return m.hexdigest()

    def _get_path(self, filename):
        return os.path.join(self.cachedir, filename)
