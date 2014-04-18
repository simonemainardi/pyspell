__author__ = 'Simone Mainardi, simonemainardi@startmail.com'

import unittest
from pprint import pprint
from pyspell import Dictionary, DictionaryItems, Word


class WordTests(unittest.TestCase):
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


class DictionaryItemsTests(unittest.TestCase):
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
        self.assertEqual(self.di.items['ciao']['suggestions']['ciaoB'], 1)
        self.assertSetEqual(set(self.di.items['ciao']['suggestions'].keys()), set(['ciaoA', 'ciaoB']))


class DictionaryTests(unittest.TestCase):
    def setUp(self):
        self.d = Dictionary()

    def test_add_word(self):
        self.d.add_word('ciao')
        ciao_deletes = Word.deletes('ciao', self.d.edit_distance_max)
        for delete in ciao_deletes:
            self.assertIn(delete, self.d.items.items)
            self.assertIn('ciao', self.d.items.items[delete]['suggestions'].keys())

        self.d.add_word('ciaoB')
        ciaoB_deletes = Word.deletes('ciaoB', self.d.edit_distance_max)
        for delete in ciaoB_deletes:
            self.assertIn(delete, self.d.items.items)
            self.assertIn('ciaoB', self.d.items.items[delete]['suggestions'].keys())

        for delete in ciao_deletes.intersection(ciaoB_deletes):
            self.assertSetEqual(set(self.d.items.items[delete]['suggestions'].keys()), set(['ciao', 'ciaoB']))

        for delete in ciao_deletes.difference(ciaoB_deletes):
            self.assertSetEqual(set(self.d.items.items[delete]['suggestions'].keys()), set(['ciao']))

        for delete in ciaoB_deletes.difference(ciao_deletes):
            self.assertSetEqual(set(self.d.items.items[delete]['suggestions'].keys()), set(['ciaoB']))


if __name__ == '__main__':
    unittest.main()
