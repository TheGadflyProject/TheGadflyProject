from spacy.en import STOPWORDS
from spacy import attrs
from collections import defaultdict
from string import punctuation
from heapq import nlargest
# http://glowingpython.blogspot.com/2014/09/text-summarization-with-nltk.html


class FrequencySummarizer:
    def __init__(self, min_cut=0.1, max_cut=0.9):
        self._min_cut = min_cut
        self._max_cut = max_cut
        self._stopwords = STOPWORDS.union(punctuation)

    def _compute_frequencies(self, word_sent):
        """
          Compute the frequency of each of word.
          Input:
           word_sent, a list of sentences already tokenized.
          Output:
           freq, a dictionary where freq[w] is the frequency of w.
        """
        freq = word_sent.count_by(attrs.ORTH)
        # frequencies normalization and fitering
        m = float(max(freq.values()))
        to_be_killed = []
        for k in freq.keys():
            freq[k] = freq[k]/m
            if freq[k] >= self._max_cut or freq[k] <= self._min_cut:
                to_be_killed.append(k)
        for k in to_be_killed:
            del freq[k]
        return freq

    def summarize(self, parsed, n):
        """
          Return a list of n sentences
          which represent the summary of text.
        """
        sents = [sent for sent in parsed.sents]
        assert n <= len(sents)

        self._freq = self._compute_frequencies(parsed)

        # Score Sentences based on token freq
        ranking = defaultdict(int)
        for i, sent in enumerate(parsed.sents):
            for w in sent:
                ranking[i] += self._freq.get(w.orth, 0)

        # Rank Sentences
        sents_idx = self._rank(ranking, n)
        top_sentences = [sents[j] for j in sents_idx]
        return top_sentences

    def _rank(self, ranking, n):
        """ return the first n sentences with highest ranking """
        return nlargest(n, ranking, key=ranking.get)
