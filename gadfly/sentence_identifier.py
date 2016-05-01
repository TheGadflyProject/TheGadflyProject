from collections import defaultdict
import math
import logging

logger = logging.getLogger("v.sent_id")


class SentenceIdentifier:
    def __init__(self, EDA):
        self.EDA = EDA
        self.sent_id_EDA_OOV = defaultdict(list)
        self.sent_id_EDA_hV = defaultdict(list)
        self.sent_id_total_score = defaultdict(int)

    def get_dict_token_probs(self, sents):
        """Get a dict of tokens and their spaCy probability"""
        dict_token_probs = dict()
        for n, sent in enumerate(sents):
            for token in sent:
                value = math.fabs(token.prob)
                dict_token_probs[(n, token)] = value
                self.sent_id_total_score[n] += value
        return dict_token_probs

    def get_ranked_sents(self, lensen, dict_token_probs):
        """(1) Get a generator of ((sent id, tokens), prob) sorted by prob
           (2) Iterate through list till 5 scores are added per sent
           (3) Rank sents by total"""

        sent_id_scores = [0] * lensen
        sent_id_score_count = [0] * lensen
        dict_token_probs_sorted = ((key, dict_token_probs[key]) for key in
                                   sorted(dict_token_probs,
                                   key=dict_token_probs.get,
                                   reverse=True))

        # Hueristics to find most important/interesting sentences:
        for (n, token), value in dict_token_probs_sorted:
            if token.like_url or token.like_email:
                continue
            elif token.like_num or token.ent_type_ in ["MONEY",
                                                       "CARDINAL",
                                                       "QUANTITY"]:
                value = 8
            elif token.orth_.startswith("@"):
                continue
            elif token.ent_type_ == "PERSON":
                continue
            elif token.ent_type_:
                print(token, token.ent_type_)
            elif token.is_oov:
                self.sent_id_EDA_OOV[n].append(token)
                continue
            elif value > 15:
                self.sent_id_EDA_hV[n].append((token, value))
                value = 15
            if sent_id_score_count[n] >= 5:
                continue
            sent_id_scores[n] = sent_id_scores[n] + value
            sent_id_score_count[n] += 1
        ranked_sents = (sorted([(x, n) for n, x in enumerate(sent_id_scores)],
                        reverse=True))
        return ranked_sents

    def get_text(self, sents):
        """Get the text itself from the spaCy object."""
        sents_text = []
        for span in sents:
            tokens = []
            for token in span:
                tokens.append(token.text)
            sents_text.append(tokens)
        return sents_text

    def identify(self, sents, n):
        """Call functions, return only the n top sentences joined"""
        dict_token_probs = self.get_dict_token_probs(sents)
        ranked_sents = self.get_ranked_sents(len(sents), dict_token_probs)

        top_sentences = []
        for score, index in ranked_sents[:n]:
            top_sentences.append(sents[index])
            if self.EDA:
                count_article_tokens = len([tkn for tkn in [
                                           sent for sent in sents]])
                logger.info("EDA:")
                logger.info("Sent: {}".format(sents[index]))
                logger.info("Score: {}".format(round(score, 2)))
                logger.info("Total Score: {}".format(round(
                                        self.sent_id_total_score[index], 2)))
                logger.info("Percent Score = {}".format(round(
                                        score / self.sent_id_total_score[
                                                index], 2)))
                logger.info("Ave. Score = {}".format(round(
                                        self.sent_id_total_score[index] / len(
                                                     sents[index]), 2)))
                logger.info("Index = {}".format(index))
                logger.info("Chars = {}".format(len(str((sents[index])))))
                logger.info("Tokens = {}".format(len(sents[index])))
                logger.info("Percent Tokens = {}".format(round(100 * (len(
                                                         sents[index]) /
                                                         count_article_tokens)
                                                         ), 5))
                logger.info("OOV: {}".format(self.sent_id_EDA_OOV[index]))
                logger.info(">15: {}".format(self.sent_id_EDA_hV[index]))
        return top_sentences
