from spacy.en import STOPWORDS
from collections import defaultdict, Counter
from string import punctuation
from heapq import nlargest
import math
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
    def __init__(self):
        pass

    def get_tokens_and_freqs(self, sents, style):
        """Get a list of all tokens in sents and a Counter of them"""
        if style == 'standard':
            all_tokens = [token.text for sent in sents for token in sent]
        elif style == 'lower':
            all_tokens = [token.lower_ for sent in sents for token in sent]
        elif style == 'lemma':
            all_tokens = [token.lemma_ for sent in sents for token in sent]
        else:
            print("Please enter an appropriate option for 'style'.")
        document_freq_dict = Counter(all_tokens)
        return document_freq_dict, all_tokens

    def get_dict_tf_idf(self, sents, document_freq_dict, all_tokens, style):
        """Get a dict of _____"""
        dict_tf_idf = {}
        for word in set(all_tokens):
            for n, sent in enumerate(sents):
                sum = 0
                if style == 'lower':
                    if word in [token.lower_ for token in sent]:
                        sum += 1
                elif style == 'lemma':
                    if word in [token.lemma_ for token in sent]:
                        sum += 1
                else:
                    if word in [token.text for token in sent]:
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
        sents_text = []
        for span in sents:
            tokens = []
            for token in span:
                tokens.append(token.text)
            sents_text.append(tokens)
        return sents_text

    def EDA(self, sents_text, dict_tf_idf):
        eda_data = defaultdict(list)
        for (index, token), value in dict_tf_idf.items():
            if value > 0:
                eda_data[index].append((round(value,2), token))
        EDA_sents_text = []
        for n, text in enumerate(sents_text):
            EDA_sents_text.append(text)
            EDA_sents_text[n] = EDA_sents_text[n] + ['\nEDA:\n'] + [str(sorted(eda_data[n], key=lambda x: x[0], reverse=True))]
        return EDA_sents_text

    def summarize(self, sents, n):
        assert n <= len(sents)
        style = 'lemma'
        document_freq_dict, all_tokens = self.get_tokens_and_freqs(sents, 
                                                                   style)
        dict_tf_idf = self.get_dict_tf_idf(sents, 
                                           document_freq_dict, 
                                           all_tokens, 
                                           style)
        ranked_sents = self.get_ranked_sents(len(sents), 
                                             dict_tf_idf)
        sents_text = self.get_text(sents)
        EDA = 0
        if EDA:
            sents_text = self.EDA(sents_text, dict_tf_idf)

        top_sentences = []
        for score, index in ranked_sents[-1:-(n+1):-1]:
            top_sentences.append(sents_text[index])

        for i in range(n):
            if top_sentences[i][0] in ['\n\n', '”','\n\n\n']: del top_sentences[i][0] # DEAL W/ THIS ELEWHERE (BUT IT REALLY ANNOYED ME) - DSG
            if top_sentences[i][0] == '\n\n': del top_sentences[i][0] # DEAL W/ THIS ELEWHERE (BUT IT REALLY ANNOYED ME) - DSG       
            top_sentences[i] = " ".join(top_sentences[i]) # THIS IS NOT SATISFACTORY BUT FINE FOR NOW, SAME AS ABOVE
        return top_sentences