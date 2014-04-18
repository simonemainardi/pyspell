__author__ = 'simone'

import unittest

from word import Word

class WordDeletesTests(unittest.TestCase):
    def test_deletes(self):
        self.assertSetEqual(Word.deletes('ciao', 3),
                            set(['iao', 'cio', 'cao', 'cia', 'co', 'ca', 'ci', 'ao', 'io', 'ia', 'c', 'i', 'a', 'o']))
        self.assertSetEqual(Word.deletes('ciao', 2),
                            set(['iao', 'cio', 'cao', 'cia', 'co', 'ca', 'ci', 'ao', 'io', 'ia']))
        self.assertSetEqual(Word.deletes('ciao', 1),
                            set(['iao', 'cio', 'cao', 'cia']))
        self.assertSetEqual(Word.deletes('ciao', 0),
                            set())
        self.assertSetEqual(Word.deletes('aaa', 30),
                            set(['aa', 'a']))
        self.assertSetEqual(Word.deletes('bbb', 3),
                            set(['bb', 'b']))
        self.assertSetEqual(Word.deletes('woho', 1),
                            set(['woh', 'oho', 'who', 'woo']))


class WordDamerauLevenstheinTests(unittest.TestCase):
    def test_damerau_levenshtein_distance(self):
        self.assertEqual(Word.damerau_levenshtein_distance('ciao', 'ciao'), 0)
        self.assertEqual(Word.damerau_levenshtein_distance('ciao', 'cia'), 1)
        self.assertEqual(Word.damerau_levenshtein_distance('cia', 'ciao'), 1)
        self.assertEqual(Word.damerau_levenshtein_distance('ciao', 'co'), 2)
        self.assertEqual(Word.damerau_levenshtein_distance('ciao', 'c'), 3)
        self.assertEqual(Word.damerau_levenshtein_distance('ciao', ''), 4)
        self.assertEqual(Word.damerau_levenshtein_distance('simone', 'siomne'), 1)
        self.assertEqual(Word.damerau_levenshtein_distance('simone', 'siomen'), 2)

class WordDistTests(unittest.TestCase):
    def setUp(self):
        self.edit_distance_max = 2
        self.shorter_words_within_distance = Word.shorter_words_within_distance
        self.words = set(['apXplYe', 'apXple', 'apple',
                          'mellon', 'melon', 'meln',
                          'pear', 'pr',
                          'orange', 'rng'])

    def test_shorter_words_within_distance(self):
        words = self.words.copy()
        res = self.shorter_words_within_distance('apXplYe', words, self.edit_distance_max)
        self.assertSetEqual(res, set(['apXple', 'apple']))
        self.assertSetEqual(words, self.words - res)

        words = self.words.copy()
        res = self.shorter_words_within_distance('apXple', words, self.edit_distance_max)
        self.assertSetEqual(res, set(['apple']))
        self.assertSetEqual(words, self.words - res)


        words = self.words.copy()
        res = self.shorter_words_within_distance('mellon', words, self.edit_distance_max)
        self.assertSetEqual(res, set(['melon', 'meln']))
        self.assertSetEqual(words, self.words - res)

        words = self.words.copy()
        res = self.shorter_words_within_distance('pear', words, self.edit_distance_max)
        self.assertSetEqual(res, set(['pr']))
        self.assertSetEqual(words, self.words - res)

        words = self.words.copy()
        res = self.shorter_words_within_distance('orange', words, self.edit_distance_max)
        self.assertSetEqual(res, set())
        self.assertSetEqual(words, self.words - res)


if __name__ == '__main__':
    unittest.main()
