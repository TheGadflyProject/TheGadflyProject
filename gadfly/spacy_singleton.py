"""
This module is to helps us manage our memory resources because it provides
a singleton wrapper around the Spacy English object to prevent it from
being instantiated overa and over again. You can access the spacy english
object by calling the function like so:
"""
import sputnik
import spacy
import os

print(spacy.about.__version__)
data_path = os.path.join(os.path.dirname(spacy.__file__), 'en', 'data')
if not os.path.isdir(data_path):
    print("Need to download Spacy data. Starting download now")
    sputnik.install('spacy', spacy.about.__version__, 'en_default', data_path=data_path)


def _spacy_en():
    yield None
    spacyen = spacy.load('en_default', via=data_path)
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
