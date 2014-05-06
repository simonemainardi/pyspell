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


class RedisStorageTests(StorageTests):
    def setUp(self):
        self.storage = RedisStorage(flush_db=True, host='localhost', port=6379, db=5)

    def tearDown(self):
        self.storage._r.flushdb()

if __name__ == '__main__':
    unittest.main()
