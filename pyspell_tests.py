__author__ = 'Simone Mainardi, simonemainardi@startmail.com'

import unittest
from storage import storage
from pyspell import OriginalTerms, SuggestTerms, Dictionary, Word

redis_host = 'localhost'
redis_port = 6379
redis_db = 5


def redis_storage():
    return storage('redis', flush_db=True, host=redis_host, port=redis_port, db=redis_db)


class TermsTests(unittest.TestCase):
    def setUp(self):
        store = storage(None)  # None means built-in dictionary storage
        self.oi = OriginalTerms(store)
        self.st = SuggestTerms(store)

    def test_original_terms(self):
        self.oi['foo'] = 1
        self.assertEqual(self.oi['foo'], 1)
        self.oi['foo'] = 2
        self.assertEqual(self.oi['foo'], 3)
        self.assertEqual(self.oi['bar'], 0)

    def test_suggest_terms(self):
        self.st['python'] = 'pythonistas'
        self.assertEqual(self.st['python'], 'pythonistas')
        self.st['python'] = 'pythons'
        self.assertEqual(self.st['python'], 'pythons')
        self.st['python'] = 'pythones'
        self.assertEqual(self.st['python'], 'pythons')


class TestTermsRedis(TermsTests):
    def setUp(self):
        store = storage('redis', flush_db=True, host=redis_host, port=redis_port, db=redis_db)
        self.oi = OriginalTerms(store)
        self.st = SuggestTerms(store)

    def tearDown(self):
        storage('redis', flush_db=True, host=redis_host, port=redis_port, db=redis_db)


class DictionaryTests(unittest.TestCase):
    def setUp(self):
        self.d = Dictionary()
        self.words = DictionaryTests.some_words()

    @staticmethod
    def some_words():
        words = ['orange', 'prange', 'rng']
        words += ['banan', 'banana', 'banans']
        words += ['aaple', 'apple', 'aple', 'aXpple', 'aXppYle']
        return words

    def test_add_word(self):
        self.d.add_word('ciao')
        ciao_deletes = Word.deletes('ciao', self.d.edit_distance_max)
        for delete in ciao_deletes:
            self.assertIn(delete, self.d._suggestions.terms)
            self.assertEqual('ciao', self.d._suggestions[delete])

        self.d.add_word('ciaoB')
        ciaoB_deletes = Word.deletes('ciaoB', self.d.edit_distance_max)
        for delete in ciaoB_deletes:
            self.assertIn(delete, self.d._suggestions.terms)
            try:
                self.assertEqual('ciaoB', self.d._suggestions[delete])
            except AssertionError:
                # collisions with deletes of ciao -- ciao is preserved in the suggestions since its shorter
                self.assertEqual('ciao', self.d._suggestions[delete])

        for delete in ciao_deletes.intersection(ciaoB_deletes):
            self.assertEqual('ciao', self.d._suggestions[delete])

        for delete in ciao_deletes.difference(ciaoB_deletes):
            self.assertEqual('ciao', self.d._suggestions[delete])

        for delete in ciaoB_deletes.difference(ciao_deletes):
            self.assertEqual('ciaoB', self.d._suggestions[delete])

    def test_lookup(self):
        # typos have been made on purpose :)
        bags = [set(['apl', 'aple', 'apple', 'applex', 'applexy']),
                set(['orange', 'rnge', 'rn']),
                set(['kiwi', 'kiwi;;', 'ki']),
                set(['watermelon', 'wassermelon', 'waxermekon'])]

        for bag in bags:
            self.d.add_words(bag)
            res = set()
            for word in bag:
                res.update(self.d.lookup(word))
            self.assertSetEqual(res, bag)

    def test_lookup_2(self):
        self.d.add_word('simone')
        self.assertSetEqual(set(['simone']), self.d.lookup('simo'))
        self.d.add_word('simon')  # a closer word arrives
        self.assertSetEqual(set(['simon']), self.d.lookup('simo'))
        self.assertSetEqual(set(['simon', 'simone']), self.d.lookup('simone'))


class DictionaryTestsRedis(DictionaryTests):
    def setUp(self):
        self.d = Dictionary(storage_type='redis', flush_db=True, host=redis_host, port=redis_port, db=redis_db)
        self.words = DictionaryTests.some_words()

    def tearDown(self):
        # flush the database via storage
        storage('redis', flush_db=True, host=redis_host, port=redis_port, db=redis_db)


if __name__ == '__main__':
    unittest.main()
