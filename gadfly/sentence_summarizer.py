from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
# http://glowingpython.blogspot.com/2014/09/text-summarization-with-nltk.html


class FrequencySummarizer:
    def __init__(self, min_cut=0.1, max_cut=0.9):
        self._min_cut = min_cut
        self._max_cut = max_cut
        self._stopwords = set(stopwords.words('english') + list(punctuation))

    def _compute_frequencies(self, word_sent):
        """
          Compute the frequency of each of word.
          Input:
           word_sent, a list of sentences already tokenized.
          Output:
           freq, a dictionary where freq[w] is the frequency of w.
        """
        freq = {}
        for s in word_sent:
            for word in s:
                if word not in self._stopwords:
                    freq.setdefault(word, 0)
                    freq[word] += 1
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

    def summarize(self, sents, n):
        """
          Return a list of n sentences
          which represent the summary of text.
        """
        assert n <= len(sents)
        self._freq = self._compute_frequencies(sents)
        # print("freq: ", self._freq)
        ranking = defaultdict(int)
        for i, sent in enumerate(sents):
            for w in sent:
                if w in self._freq:
                    ranking[i] += self._freq[w]
        sents_idx = self._rank(ranking, n)
        return [sents[j] for j in sents_idx]

    def _rank(self, ranking, n):
        """ return the first n sentences with highest ranking """
        return nlargest(n, ranking, key=ranking.get)
