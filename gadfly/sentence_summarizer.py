from spacy.en import STOPWORDS
from collections import defaultdict, Counter
from string import punctuation
from heapq import nlargest
import math
import re
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
        top_sentences = [sents[j] for j in sents_idx]
        for i in range(len(top_sentences)):
            top_sentences[i] = " ".join(top_sentences[i])
        return top_sentences

    def _rank(self, ranking, n):
        """ return the first n sentences with highest ranking """
        return nlargest(n, ranking, key=ranking.get)


class TF_IDFSummarizer:
    def __init__(self, style, EDA):
        self.EDA = EDA
        self.style = style.value

    def get_tokens_and_freqs(self, sents, style):
        """Get a list of all tokens in sents and a Counter of them"""
        all_tokens = [getattr(token, style) for sent in sents for token in sent]
        document_freq_dict = Counter(all_tokens)
        return document_freq_dict, all_tokens

    def get_dict_tf_idf(self, sents, document_freq_dict, all_tokens, style):
        """Get a dict of tokens and their tf/idf score"""
        dict_tf_idf = {}
        for word in set(all_tokens):
            for n, sent in enumerate(sents):
                sum = 0
                if word in [getattr(token, style) for token in sent]:
                    sum += 1
                dict_tf_idf[(n, word)] = sum * math.log(len(sents)/document_freq_dict[word])
        return dict_tf_idf

    def get_ranked_sents(self, lensen, dict_tf_idf):
        n_scores = [0] * lensen
        for (n, word), value in dict_tf_idf.items():
            n_scores[n] = n_scores[n] + value
        ranked_sents = (sorted([(x, n) for n, x in enumerate(n_scores)]))
        return ranked_sents

    def get_text(self, sents):
        """Get the text itself from the spacy object."""
        sents_text = []
        for span in sents:
            tokens = []
            for token in span:
                tokens.append(token.text)
            sents_text.append(tokens)
        return sents_text

    def create_EDA(self, sents_text, dict_tf_idf):
        """create EDA data. EDA must be True when calling TF_IDFSummarizer."""
        eda_data = defaultdict(list)
        score = {}
        for (index, token), value in dict_tf_idf.items():
            if value > 0:
                eda_data[index].append((round(value,2), token))
            score.setdefault(index, 0)
            score[index] += value
        EDA_sents_text = []
        for n, text in enumerate(sents_text):
            EDA_sents_text.append(text)
            EDA_sents_text[n] = EDA_sents_text[n] + ['\nEDA: \n'] + [str(score[n]), 
                                                                    str(sorted(eda_data[n], 
                                                                    key=lambda x: x[0], 
                                                                    reverse=True))]
        return EDA_sents_text

    def summarize(self, sents, n):
        """Call functions, return only the n top sentences joined"""
        assert n <= len(sents)
        document_freq_dict, all_tokens = self.get_tokens_and_freqs(sents, self.style)
        dict_tf_idf = self.get_dict_tf_idf(sents, document_freq_dict, all_tokens, self.style)
        ranked_sents = self.get_ranked_sents(len(sents), dict_tf_idf)
        
        sents_text = self.get_text(sents)
        
        if self.EDA:
            EDA_sents_text = self.create_EDA(sents_text, dict_tf_idf)
            f = open("EDA.txt", "a", encoding='utf-8')
            for n, each in enumerate(EDA_sents_text):
                f.write("Sentence {} of {}\n".format(n+1, len(EDA_sents_text)))
                f.write(str(" ".join(each)))
                f.write("\n\n")
            f.close()

        top_sentences = []
        for score, index in ranked_sents[-1:-(n+1):-1]:
            top_sentences.append(sents_text[index])

        for i in range(n):
            top_sentences[i] = " ".join(top_sentences[i])
        return top_sentences