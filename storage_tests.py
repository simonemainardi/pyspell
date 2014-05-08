__author__ = 'simone'

import unittest
from storage import RedisStorage, DictStorage


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.storage = DictStorage()

    def test(self):
        self.storage['hello'] = 1

        self.assertIn('hello', self.storage)
        self.assertEqual(1, int(self.storage['hello']))
        self.assertEqual(2, self.storage.incrby('hello', 1))
        self.assertEqual(5, self.storage.incrby('hello', 3))
        self.storage['hello'] = 1
        self.assertEqual(1, int(self.storage['hello']))

        self.storage['ciao'] = 'hallo'
        self.assertEqual('hallo', self.storage['ciao'])
        self.assertRaises(ValueError, lambda: self.storage.incrby('ciao', 1))
        self.storage['ciao'] = 'hullo'
        self.assertEqual('hullo', self.storage['ciao'])

    def test_set_features(self):
        fruits = set(['apple', 'banana', 'kiwi', 1, 2, 3])
        for fruit in fruits:
            self.storage.sadd('fruit', fruit)
        self.assertSetEqual(fruits, self.storage.smembers('fruit'))
        self.storage.sclear('fruit')
        self.assertSetEqual(set(), self.storage.smembers('fruit'))

class RedisStorageTests(StorageTests):
    def setUp(self):
        self.storage = RedisStorage(flush_db=True, host='localhost', port=6379, db=5)

    def tearDown(self):
        self.storage._r.flushdb()

if __name__ == '__main__':
    unittest.main()
