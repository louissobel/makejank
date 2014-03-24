"""
Cache interface

 - get(key)
 - last_modified(key) --> None (if not exists) or last modified in unix
 - put (key, value)
"""

class FilesystemCache(object):

    def __init__(self, cachedir):
        pass

    def last_modified(self, key):
        pass

    def get(self, key):
        pass

    def put(self, key, value):
        pass


    