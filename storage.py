__author__ = 'Simone Mainardi, simonemainardi@startmail.com'

import abc
import redis


class Storage(object):
    @abc.abstractmethod
    def __init__(self, flush_db=False, **kwargs):
        """
        Initializes an object to store values. If the storage needs a database connection, it also
        connects to the database.
        """
        return

    @abc.abstractmethod
    def __getitem__(self, item):
        """
        Looks for the `item` and possibly returns its value. None is returned if `item` is not present.
        """
        return

    @abc.abstractmethod
    def __setitem__(self, key, value):
        """
        Stores `value` as the value of item  named `key`. If `key` is not present it is added to the storage.
        If `key` contained an old value, the old value is overwritten.
        """
        return

    def incrby(self, key, incr):
        if not self[key]:
            self[key] = 0
        self[key] = int(self[key]) + incr
        return int(self[key])


class RedisStorage(Storage):
    def __init__(self, flush_db=False, **kwargs):
        r = redis.StrictRedis(**kwargs)
        if flush_db:
            r.flushdb()
        self._r = r

    def __getitem__(self, key):
        return self._r.get(key)

    def __setitem__(self, key, value):
        self._r.set(key, value)

    def __contains__(self, key):
        return True if self._r.get(key) else False


class DictStorage(Storage):
    def __init__(self):
        self._items = dict()

    def __getitem__(self, key):
        return self._items[key] if key in self._items else None

    def __setitem__(self, key, value):
        self._items[key] = value

    def __contains__(self, key):
        return key in self._items