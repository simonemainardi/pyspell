# pyspell

A fast pure-python spell checking algorithm. Seriously, it's really fast. And supports Redis.

## Features

`pyspell` quickly finds the best suggestions of a word. Suggestions are stored in a dictionary and can be dynamically updated. The dictionary can be initialized using, for example, a text book. Word frequencies in the text are taken into account to return the most accurate suggestions.

## Examples
Suppose we want to initialize our dictionary with a book. Let's download _Moby Dick_ from _Project Gutenberg_.
```python
>>> import urllib
>>> import re, string
>>> 
>>> book = urllib.urlopen('http://www.gutenberg.org/cache/epub/2701/pg2701.txt').read()
>>> pattern = re.compile('[\W_]+')  # alpha-num only
>>> book = pattern.sub(' ', book).lower().split()  # lower case
```
Using the book as a dictionary for pyspell is as simple as:
```python
>>> from pyspell import Dictionary
>>> d = Dictionary()
>>> d.add_words(book)
```
