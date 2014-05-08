__author__ = 'Simone Mainardi, simonemainardi@startmail.com'

import codecs
from word import Word
from storage import storage


def prepender(func):
    """
    Prepends some text to the *second* argument with which function `func` has been called.
    The *first* argument is a reference (`self`) to an instance of class Terms or one of its sub classes.
    `self` is accessed to look for a prefix `_prefix` to append to the second argument.

    This function is meant to be used as decorator.
    """
    def prepend(self, *args):
        prepended = self._prefix + args[0]
        return func(self, prepended, *args[1:])
    return prepend


class Terms(object):
    def __init__(self, store=None):
        self._items = store

    @property
    def terms(self):
        """
        Returns all the terms we have stored without their prefix
        """
        return [k[len(self._prefix):] for k in self._items.keys() if k.startswith(self._prefix)]


class OriginalTerms(Terms):
    _prefix = 't:'  # this prefix stands for `term:`

    @prepender
    def __setitem__(self, word, count):
        """
        Adds the `word` to the original terms. The number of occurrences is specified in `count`.
        """
        self._items.incrby(word, count)

    @prepender
    def __getitem__(self, word):
        """
        Returns the number of occurrences of `word` in the corpus or 0 if it wasn't present.
        """
        return self._items[word] if word in self._items else 0


class SuggestTerms(Terms):
    _prefix = 's:'  # this prefix stands for `suggestion:`

    @prepender
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

    @prepender
    def __getitem__(self, word):
        return self._items[word] if word in self._items else None


class Dictionary(object):
    def __init__(self, edit_distance_max=2, best_suggestion_only=False, storage_type=None, **kwargs):
        store = storage(storage_type, **kwargs)
        self._terms = OriginalTerms(store)
        self._suggestions = SuggestTerms(store)
        self.edit_distance_max = edit_distance_max
        self.best_suggestion_only = best_suggestion_only

    def add_word(self, word):
        self._terms[word] = 1
        for delete in Word.deletes(word, self.edit_distance_max):
            self._suggestions[delete] = word

    def add_words(self, words):
        for word in words:
            self.add_word(word)

    def initialize(self, text):
        """ Initializes the dictionary using the `text` provided.
        """
        with codecs.open(text, encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                self.add_word(word)

    def lookup(self, word, return_distances=False):
        if self._terms[word] > 0 and self.best_suggestion_only:  # there is an exact match in the dictionary
            return [word]

        results = set()
        candidates = set([(word, 0)])  # a set of tuples (candidate, candidate_distance)
        for delete in Word.deletes(word, self.edit_distance_max):
            delete_distance = len(word) - len(delete)
            candidates.update([(delete, delete_distance)])
        candidates = sorted(candidates, key=lambda x: x[1])  # sort by increasing distance

        print "candidates=", candidates

        while candidates:
            candidate, candidate_distance = candidates.pop()  # the distance of the candidate from `word`
            candidate_count = self._terms[candidate]  # the (possibly 0) no. of occurrences for candidate
            if candidate_count > 0:  # there is an entry for this item in the dictionary
                #  candidate is an original word!
                results.update([(candidate, candidate_distance)])
                print "candidate count > 0: results=", results
            suggestion = self._suggestions[candidate]  # the (possibly not existing) suggestion for candidate
            if suggestion and not suggestion in [r[0] for r in results]:  # the suggestion exists and hasn't been found
                if suggestion == word:  # by chance, the suggestion is actually the word we are looking for
                    real_distance = 0
                elif candidate_distance == 0:  # candidate _is_ the word we are looking up for
                    real_distance = len(suggestion) - len(candidate)  # suggestion_distance
                else:  # candidate is a delete edit of the word we are looking up for
                    real_distance = Word.damerau_levenshtein_distance(word, suggestion)
                if real_distance <= self.edit_distance_max:
                    results.update([(suggestion, real_distance)])
                print "suggestion found for candidate %s : results=%s" % (candidate, results)
        # sort the results first by increasing distance, then by decreasing frequency
        print "BEFORE=", results
        results = sorted(list(results), key=lambda r: (r[1], -self._terms[r[0]]))
        if not return_distances:
            results = [r[0] for r in results]  # pop out the distances and keep only the suggestions
        print "AFTER=", results
        return results


if __name__ == '__main__':
    pass
