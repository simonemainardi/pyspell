__author__ = 'Simone Mainardi, simonemainardi@startmail.com'

import abc
import redis

__all__ = ['storage']


def storage(storage_type, **kwargs):
    if not storage_type:
        return DictStorage()
    elif storage_type == 'redis':
        return RedisStorage(**kwargs)
    else:
        raise ValueError('storage_type not supported.')


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
        if key not in self:
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
        val = self._r.get(key)
        try:
            return int(val)
        except ValueError:
            return val

    def __setitem__(self, key, value):
        self._r.set(key, value)

    def __contains__(self, key):
        return True if self._r.get(key) else False

    def smembers(self, key):
        """
        Get all the members in a set.
        """
        res = self._r.smembers(key)
        return set([int(el) if el.isdigit() else el for el in res])  # possibly convert values to integers

    def sadd(self, key, value):
        """
        Insert a `value` into a set.
        """
        self._r.sadd(key, value)

    def sclear(self, key):
        """
        Clear the contents of a set
        """
        self._r.delete(key)

    def keys(self):
        return self._r.keys()

class DictStorage(Storage):
    def __init__(self):
        self._items = dict()

    def __getitem__(self, key):
        return self._items[key] if key in self._items else None

    def __setitem__(self, key, value):
        self._items[key] = value

    def __contains__(self, key):
        return key in self._items

    def smembers(self, key):
        """
        Get all the members in a set.
        """
        return self._items[key] if key in self._items else set()

    def sadd(self, key, value):
        """
        Insert a `value` into a set.
        """
        if not key in self._items:
            self._items[key] = set([value])
        else:
            self._items[key].update([value])

    def sclear(self, key):
        """
        Clear the contents of a set
        """
        self._items[key].clear()

    def keys(self):
        return self._items.keys()