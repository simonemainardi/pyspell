__author__ = 'Simone Mainardi, simonemainardi@startmail.com'

import codecs


class Word(object):
    @staticmethod
    def deletes(word, edit_distance):
        """ Recursively create all the possible deletes at a distance * less than or equal to * `edit_distance`
        from the `word` provided. For example, all the possible delete edits of the word `ciao`, at an
        edit distance less than or equal to two are:
        -> cia, cao, cio, iao (distance 1)
        -> ci, ia, ca, ca, ao, co, ci, io, co, ia, ao, io (distance 2)

        Duplicates are suppressed.
        """
        dels = set()
        if len(word) <= 1 or edit_distance == 0:
            return dels
        for i in range(len(word)):
            delete = word[:i] + word[i+1:]  # remove the i-th character from the word
            dels.update([delete])
            dels.update(Word.deletes(delete, edit_distance - 1))
        return dels


class DictionaryItems(object):
    def __init__(self):
        self.items = {}  # it might be

    def __setitem__(self, word, term):
        self.items.setdefault(word, {'term': term})  # only `term` by default
        if self.items[word]['term'] == '':
            # overwrite 'term' only if it was empty, since it can become a real term
            self.items[word]['term'] = term
        if term != '':  # count the number of real terms (and not artificially generated deletes that have '' here)
            self.items[term].setdefault('count', 0)
            self.items[term]['count'] += 1

    def add_suggestion(self, delete, original, distance):
        self.__setitem__(delete, '')  # no term for deletes
        self.items[delete].setdefault('suggestions', {})
        self.items[delete]['suggestions'][original] = distance


class Dictionary(object):
    def __init__(self, edit_distance_max=2):
        self.items = DictionaryItems()
        self.edit_distance_max = edit_distance_max

    def add_word(self, word):
        self.items[word] = word
        for delete in Word.deletes(word, self.edit_distance_max):
            distance = len(word) - len(delete)  # the distance of the current delete term from the original word
            self.items.add_suggestion(delete, word, distance)

    def initialize(self, dictionary_file):
        """ Initializes the dictionary using the `dictionary_file` provided, which is
        simply a word list, one word per line.
        """
        with codecs.open(dictionary_file, encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                self.add_word(word)


class MongoDictionary(Dictionary):
    def __init__(self, host, port, db, collection):
        pass


class PySpell(object):
    def __init__(self, dictionary_storage=None):
        self.dictionary = {}


if __name__== '__main__':
    pass
