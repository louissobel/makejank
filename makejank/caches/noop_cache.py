"""
A Fake Cache that doesn't do shit
"""

class NoopCache(object): # pragma: no cover

    def get(*args):
        return None

    def put(*args):
        pass

    def last_modified(*args):
        return None
    