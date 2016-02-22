import nltk


class Chunker:

    def _chunk(self, sentence, grammar):
        """ Identifies noun phrases """
        cp = nltk.RegexpParser(grammar)
        result = cp.parse(sentence)
        return result

    def noun_phrase_chunker(self, sentence):
        """ Identifies noun phrases """
        grammar = "NP: {<CD>*(((<JJ.*>|<N.*>)+(<N.*>|<CD>)*)|<N.*>)}"
        return self._chunk(sentence, grammar)

    def proper_noun_phrase_chunker(self, sentence):
        proper_noun_grammar = "NNP: {(<NNP.*>)+}"
        return self._chunk(sentence, proper_noun_grammar)

    def extended_proper_noun_phrase_chunker(self, sentence):
        """ Identifies noun phrases """
        grammar = "NP: {(<DT>)*((<JJ.*>)*(<NNP.*>(<CC><NNP.*>)*)+(<NN.*>)*)}"
        return self._chunk(sentence, grammar)
