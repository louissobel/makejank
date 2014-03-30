"""
A couple of caches
 - filesystem
 - memory

part of the cache contract is that they are allowed
to just drop keys

this is obviously different semantics than a key value store
"""
from memory_cache import MemoryCache
from filesystem_cache import FilesystemCache
from testing_cache import TestingCache
from noop_cache import NoopCache