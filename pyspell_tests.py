__author__ = 'Simone Mainardi, simonemainardi@startmail.com'

import unittest
from pprint import pprint
from pyspell import OriginalTerms, SuggestTerms, Dictionary, Word


class TermsTests(unittest.TestCase):
    def setUp(self):
        self.oi = OriginalTerms()
        self.st = SuggestTerms()

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


class DictionaryItemsTests():
    def setUp(self):
        self.di = DictionaryItems()

    def test_set_item(self):
        self.di['cia'] = ''  # an empty `term` for delete-edited words such as `cia` for and `ciao`
        self.assertIn('cia', self.di.items)
        self.assertEqual(self.di.items['cia']['term'], '')
        self.assertListEqual(self.di.items['cia'].keys(), ['term'])

        self.di['cia'] = 'cia'  # now assume that `cia` is also a word in the dictionary and not only a delete
        self.assertIn('cia', self.di.items)
        self.assertEqual(self.di.items['cia']['term'], 'cia')
        self.assertSetEqual(set(self.di.items['cia'].keys()), set(['term', 'count']))

        self.di['cia'] = 'cia'  # one more occurrence of 'cia' in the corpus...
        self.assertEqual(self.di.items['cia']['count'], 2)

    def test_add_suggestions(self):
        self.di.add_suggestion('ciao', 'ciaoA', 1)
        self.assertEqual(self.di.items['ciao']['term'], '')
        self.assertEqual(self.di.items['ciao']['suggestions']['ciaoA'], 1)

        self.di.add_suggestion('ciao', 'ciaoB', 1)
        self.assertEqual(self.di.items['ciao']['term'], '')
        # ciaoB is not inserted as a suggestion since there is already ciaoA which has the same distance from ciao
        self.assertSetEqual(set(self.di.items['ciao']['suggestions'].keys()), set(['ciaoA']))


class DictionaryTests(unittest.TestCase):
    def setUp(self):
        self.d = Dictionary()
        self.words = ['orange', 'prange', 'rng']
        self.words += ['banan', 'banana', 'banans']
        self.words += ['aaple', 'apple', 'aple', 'aXpple', 'aXppYle']

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

if __name__ == '__main__':
    unittest.main()
