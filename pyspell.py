__author__ = 'Simone Mainardi, simonemainardi@startmail.com'

import codecs
from word import Word


class Terms(object):
    def __init__(self):
        self._items = {}

    @property
    def terms(self):
        return self._items.keys()


class OriginalTerms(Terms):
    def __setitem__(self, word, count):
        """
        Adds the `word` to the original terms. The number of occurrences is specified in `count`.
        """
        self._items.setdefault(word, 0)
        self._items[word] += count

    def __getitem__(self, word):
        """
        Returns the number of occurrences of `word` in the corpus or 0 if it wasn't present.
        """
        return self._items[word] if word in self._items else 0


class SuggestTerms(Terms):
    def __setitem__(self, delete, suggestion):
        """
        Adds the `delete` term with the corresponding `suggestion`.
        """
        # Damerau-Levenshtein distance can be trivially inferred since `delete` is obtained
        # by deleting one or more characters from suggestion.
        if delete not in self._items or len(suggestion) < len(self._items[delete]):
            # if delete is not present in the delete terms OR
            # if the new suggestion` has a smaller Damerau-Levenshtein distance from `delete`
            # we create/modify the entry.
            # The new `suggestion` has a smaller Damerau-Levenshtein distance if:
            # len(suggestion) - len(delete) < len(self._items[delete]) - len(delete)
            # if we simplify on len(delete) on both sides, we obtain the second condition in the above if statement.
            self._items[delete] = suggestion

    def __getitem__(self, word):
        return self._items[word] if word in self._items else None


class Dictionary(object):
    def __init__(self, edit_distance_max=2):
        self._terms = OriginalTerms()
        self._suggestions = SuggestTerms()
        self.edit_distance_max = edit_distance_max

    def add_word(self, word):
        self._terms[word] = 1
        for delete in Word.deletes(word, self.edit_distance_max):
            self._suggestions[delete] = word

    def add_words(self, words):
        for word in words:
            self.add_word(word)

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
            candidate_count = self._terms[candidate]  # the (possibly 0) no. of occurrences for candidate
            if candidate_count > 0:  # there is an entry for this item in the dictionary
                #  candidate is an original word!
                results.update([candidate])
            suggestion = self._suggestions[candidate]  # the (possibly not existing) suggestion for candidate
            if suggestion and not suggestion in results:  # if the suggestion exists and has not yet been found
                if suggestion == word:  # by chance, the suggestion is actually the word we are looking for
                    real_distance = 0
                elif candidate_distance == 0:  # candidate _is_ the word we are looking up for
                    real_distance = len(suggestion) - len(candidate)  # suggestion_distance
                else:  # candidate is a delete edit of the word we are looking up for
                    real_distance = Word.damerau_levenshtein_distance(candidate, suggestion)
                if real_distance <= self.edit_distance_max:
                    results.update([suggestion])
        return results


if __name__ == '__main__':
    pass
