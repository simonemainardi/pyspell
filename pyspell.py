__author__ = 'Simone Mainardi, simonemainardi@startmail.com'

import codecs
from word import Word


class DictionaryItems(object):
    def __init__(self):
        self.items = {}  # it might be

    def __getitem__(self, word):
        return self.items[word] if word in self.items else {}

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
        distances = self.items[delete]['suggestions'].values()  # it may be an empty list
        if not distances or (distances and distance < min(distances)):  # keep only the minimum distance
            self.items[delete]['suggestions'].clear()
            self.items[delete]['suggestions'][original] = distance


class Dictionary(object):
    def __init__(self, edit_distance_max=2):
        self.items = DictionaryItems()
        self._words = set()
        self.edit_distance_max = edit_distance_max

    def add_word(self, word):
        self._words.update([word])
        self.items[word] = word
        for delete in Word.deletes(word, self.edit_distance_max):
            distance = len(word) - len(delete)  # the distance of the current delete term from the original word
            self.items.add_suggestion(delete, word, distance)

    def add_words(self, words):
        for word in words:
            self.add_word(word)

    @property
    def words(self):
        return list(self._words)

    def initialize(self, dictionary_file):
        """ Initializes the dictionary using the `dictionary_file` provided, which is
        simply a word list, one word per line.
        """
        with codecs.open(dictionary_file, encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                self.add_word(word)

    def lookup(self, word):
        results = set()
        candidates = set([(word, 0)])  # a set of tuples (candidate, candidate_distance)
        for delete in Word.deletes(word, self.edit_distance_max):
            delete_distance = len(word) - len(delete)
            candidates.update([(delete, delete_distance)])
        candidates = sorted(candidates, key=lambda (x): -x[1])  # sort according to an increasing distance

        while candidates:
            candidate, candidate_distance = candidates.pop()  # the distance of the candidate from `word`
            candidate_item = self.items[candidate]  # the (possibly empty) dictionary entry for candidate
            if candidate_item:  # there is an entry for this item in the dictionary
                if candidate_item['term'] != '':  # candidate is an original word!
                    results.update([candidate_item['term']])
                if 'suggestions' in candidate_item:
                    for suggestion, suggestion_distance in candidate_item['suggestions'].items():
                        if suggestion in results:
                            continue  # early skip suggestions already found
                        if suggestion == word:  # by chance, the suggestion is actually the word we are looking for
                            real_distance = 0
                        elif candidate_distance == 0:  # candidate _is_ the word we are looking up for
                            real_distance = suggestion_distance
                        else:  # candidate is a delete edit of the word we are looking up for
                            real_distance = Word.damerau_levenshtein_distance(candidate, suggestion)
                        if real_distance <= self.edit_distance_max:
                            results.update([suggestion])
        return results





class MongoDictionary(Dictionary):
    def __init__(self, host, port, db, collection):
        pass


class PySpell(object):
    def __init__(self, dictionary_storage=None):
        self.dictionary = {}


if __name__== '__main__':
    pass
