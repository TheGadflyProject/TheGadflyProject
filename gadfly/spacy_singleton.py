"""
This module is to helps us manage our memory resources because it provides
a singleton wrapper around the Spacy English object to prevent it from
being instantiated overa and over again. You can access the spacy english
object by calling the function like so:



"""

from spacy.en import English


def _spacy_en():
    yield None
    spacyen = English()
    while True:
        yield spacyen

_SPACY_EN = _spacy_en()


def spacy_en():
    """
    """
    spacyen = next(_SPACY_EN)
    if spacyen:
        return spacyen
    else:
        return spacy_en()
