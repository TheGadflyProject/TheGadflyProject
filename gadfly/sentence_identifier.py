from collections import defaultdict
import math
import logging

logger = logging.getLogger("v.sent_sum")


class SentenceIdentifier:
    def __init__(self, EDA):
        self.EDA = EDA

    def get_dict_tf_idf(self, sents):
        """Get a dict of tokens and their tf/idf score"""
        dict_tf_idf = {}
        for n, sent in enumerate(sents):
            for token in sent:
                dict_tf_idf[(n, token.text)] = math.fabs(token.prob)
        return dict_tf_idf

    def get_ranked_sents(self, lensen, dict_tf_idf):
        n_scores = [0] * lensen
        n_score_count = [0] * lensen
        dict_tf_idf_sorted = ((k, dict_tf_idf[k]) for k in sorted(dict_tf_idf,
                              key=dict_tf_idf.get,
                              reverse=True))
        for (n, word), value in dict_tf_idf_sorted:
            if n_score_count[n] >= 5:
                continue
            n_scores[n] = n_scores[n] + value
            n_score_count[n] += 1
        ranked_sents = (sorted([(x, n) for n, x in enumerate(n_scores)],
                        reverse=True))
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
                eda_data[index].append((round(value, 2), token))
            score.setdefault(index, 0)
            score[index] += value
        EDA_sents_text = []
        for n, text in enumerate(sents_text):
            EDA_sents_text.append(text)
            EDA_sents_text[n] = EDA_sents_text[n] + ['\nEDA: \n'] + \
                [str(sum([a for (a, b) in
                 sorted(eda_data[n],
                 key=lambda x: x[0],
                 reverse=True)][:5]))+"\n",
                 str(sorted(eda_data[n], key=lambda x: x[0], reverse=True))]
        return EDA_sents_text

    def identify(self, sents, n):
        """Call functions, return only the n top sentences joined"""
        dict_tf_idf = self.get_dict_tf_idf(sents)
        ranked_sents = self.get_ranked_sents(len(sents), dict_tf_idf)

        if self.EDA:
            sents_text = self.get_text(sents)
            EDA_sents_text = self.create_EDA(sents_text, dict_tf_idf)
            f = open("EDA.txt", "a", encoding='utf-8')
            for n_, each in enumerate(EDA_sents_text):
                f.write("Sentence {} of {}\n".format(n_+1,
                                                     len(EDA_sents_text)))
                f.write(str(" ".join(each)))
                f.write("\n\n")
            f.close()

        top_sentences = []
        for score, index in ranked_sents[:n]:
            top_sentences.append(sents[index])
        return top_sentences
