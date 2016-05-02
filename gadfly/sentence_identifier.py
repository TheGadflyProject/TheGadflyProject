from collections import defaultdict
from scipy.stats import rankdata
import numpy
import logging
from textstat.textstat import textstat


logger = logging.getLogger("v.sent_id")


class SentenceFeatures:
    def __init__(self, sents, index):
        self._exclude_named_ent_types = ["DATE", "TIME", "PERCENT", "CARDINAL",
                                         "MONEY", "ORDINAL", "QUANTITY", ""]
        self.article = sents
        self.sent = sents[index]
        self.text = "".join(token.text_with_ws for token in self.sent)
        self.score_ranking = None
        self.index = index
        self.index_rank = None
        self.char_count = len(str(self.sent))
        self.char_count_rank = None
        self.token_count = len(self.sent)
        self.token_count_rank = None
        self.log_prob_list = list()
        self.total_log_prob = 0
        self.total_log_prob_rank = None
        self.taken_log_prob = 0
        self.taken_log_prob_rank = None
        self.taken_of_total_log_prob_percent = None
        self.taken_of_log_prob_percent = 0
        self.taken_of_log_prob_percent_rank = None
        self.ent_types_count = defaultdict(int)
        self.out_of_vocab_list = list()
        self.low_log_prob_list = list()
        self.low_log_prob_count_rank = None
        self.ent_count = 0
        self.ent_count_rank = None

        self.has_named_entity = self.set_has_named_entity()

        self.smog_index = textstat.smog_index(self.text)
        self.syllable_count = textstat.syllable_count(self.text)
        self.gunning_fog = textstat.gunning_fog(self.text)
        self.linsear_write_formula = textstat.linsear_write_formula(self.text)
        self.coleman_liau_index = textstat.coleman_liau_index(self.text)
        self.automated_readability_index = textstat.\
            automated_readability_index(self.text)

        if len(self.article) >= 20:
            cutoff = 10
        else:
            cutoff = int(len(self.article)/2)
        self.similarity_first10 = numpy.mean([self.sent.similarity(sent) for
                                              index, sent in enumerate(
                                              self.article[:cutoff]) if index
                                              is not self.index])
        self.similarity_last10 = numpy.mean([self.sent.similarity(sent) for
                                             index, sent in enumerate(
                                             self.article[-cutoff:]) if index
                                             is not self.index])
        if self.index == 0:
            self.similarity_previous = None
        else:
            self.similarity_previous = self.sent.similarity(
                                            self.article[self.index-1])
        if self.index + 1 == len(self.article):
            self.similarity_next = 0
        else:
            self.similarity_next = self.sent.similarity(self.article[
                                            self.index+1])
        self.similarity_all_but = numpy.mean([self.sent.similarity(sent) for
                                              index, sent in enumerate(
                                              self.article) if index is
                                              not self.index])

    def set_ranks(self, article_object):
        self.index_rank = self.index / len(self.article)
        self.char_count_rank = list(
            rankdata(article_object.char_counts))[self.index] /\
            len(self.article)
        self.token_count_rank = list(
            rankdata(article_object.char_counts))[self.index] /\
            len(self.article)
        self.total_log_prob_rank = list(
            rankdata(article_object.total_log_probs))[self.index] /\
            len(self.article)
        self.taken_log_prob_rank = list(
            rankdata(article_object.taken_log_probs))[self.index] /\
            len(self.article)
        self.low_log_prob_count_rank = list(
            rankdata(article_object.low_log_prob_counts))[self.index] /\
            len(self.article)
        self.ent_count_rank = list(
            rankdata(article_object.ent_counts))[self.index] /\
            len(self.article)
        self.taken_of_log_prob_percent_rank = list(
            rankdata(article_object.taken_of_log_prob_percents))[self.index] /\
            len(self.article)

    def set_score_ranking(self):
        if self.has_named_entity:
            self.score_ranking = self.index_rank + self.taken_log_prob
        else:
            self.score_ranking = None

    def set_log_probs(self):
        """
        (1) set total log probability by token
        (2) create out_of_vocab_list
        (3) create low_log_prob_list
        (4) create ent_types_count dict
        (5) set ent_count
        (6) create log_prob_list
        (7) create taken_log_prob
        (8) create taken_of_log_prob_percent
        """
        for token, log_prob in [(token, token.prob) for token in self.sent]:
            self.total_log_prob += log_prob
            if token.ent_type_ is not "":
                self.ent_types_count[token.ent_type_] += 1
            if token.ent_type_ not in self._exclude_named_ent_types:
                self.ent_count += 1
            if token.like_url or token.like_email:
                continue
            elif token.like_num or token.ent_type_ in ["MONEY",
                                                       "CARDINAL",
                                                       "QUANTITY"]:
                log_prob = -5
            elif token.orth_.startswith("@"):
                continue
            elif token.ent_type_ == "PERSON":
                continue
            elif token.is_oov:
                self.out_of_vocab_list.append(token)
                continue
            elif log_prob < -15:
                self.low_log_prob_list.append((token, log_prob))
            self.log_prob_list.append(log_prob)
        self.taken_log_prob = sum(sorted(
            [prob if prob >= -15 else -15 for prob in self.log_prob_list])[:5])
        if self.taken_log_prob != 0:
            self.taken_of_log_prob_percent = self.taken_log_prob /\
                                             self.total_log_prob

    def set_has_named_entity(self):
        for token in self.sent:
            if token.ent_type_ not in self._exclude_named_ent_types:
                return True
        return False


class ArticleFeatures:
    def __init__(self, sent_objects):
        self.char_counts = [s.char_count for s in sent_objects]
        self.token_counts = [s.token_count for s in sent_objects]
        self.total_log_probs = [s.total_log_prob for s in sent_objects]
        self.taken_log_probs = [s.taken_log_prob for s in sent_objects]
        self.low_log_prob_counts = [len(s.low_log_prob_list) for s in
                                    sent_objects]
        self.ent_counts = [s.ent_count for s in sent_objects]

        self.has_named_entity_list = [True if s.has_named_entity
                                      else False for s in sent_objects]
        self.has_named_entity_count = sum(self.has_named_entity_list)
        self.taken_of_log_prob_percents = [s.taken_of_log_prob_percent for s in
                                           sent_objects]


class SentenceIdentifier:
    def __init__(self):
        self.sents = None
        self.return_n = None

    def get_ranked_sents(self):
        ranked_sents = list()
        for s in self.sent_objects:
            if s.score_ranking:
                ranked_sents.append((s.score_ranking, s))
        return [s for rank, s in sorted(ranked_sents)][:self.return_n]

    def identify(self, sents, n):
        """Call functions, return only the n top sentences joined"""
        self.sents = sents
        self.return_n = n
        self.sent_objects = [SentenceFeatures(sents, index) for index, sent
                             in enumerate(sents)]

        [s.set_log_probs() for s in self.sent_objects]
        article_object = ArticleFeatures(self.sent_objects)
        [s.set_ranks(article_object) for s in self.sent_objects]
        [s.set_score_ranking() for s in self.sent_objects]

        top_sentence_objects = self.get_ranked_sents()
        top_sentences = [s.sent for s in top_sentence_objects]

        for s in top_sentence_objects:
            logger.info("EDA:")
            logger.info("sent: {}".format(s.sent))
            logger.info("has_named_entity: {}".format(s.has_named_entity))
            logger.info("score_ranking: {}".format(s.score_ranking))
            # logger.info("index: {}".format(s.index))
            # logger.info("index_rank: {}".format(s.index_rank))
            # logger.info("char_count {}".format(s.char_count))
            # logger.info("char_count_rank {}".format(s.char_count_rank))
            # logger.info("token_count = {}".format(s.token_count))
            # logger.info("token_count_rank = {}".format(s.token_count_rank))
            # logger.info("log_prob_list: {}".format(s.log_prob_list))
            # logger.info("total_log_prob: {}".format(s.total_log_prob))
            # logger.info("total_log_prob_rank: {}".format(
            #                         s.total_log_prob_rank))
            # logger.info("taken_log_prob: {}".format(
            #                         s.taken_log_prob))
            # logger.info("taken_log_prob_rank: {}".format(
            #                         s.taken_log_prob_rank))
            # logger.info("low_log_prob_count_rank: {}".format(
            #                         s.low_log_prob_count_rank))
            # logger.info("ent_count: {}".format(s.ent_count))
            # logger.info("ent_count_rank: {}".format(s.ent_count_rank))
            # logger.info("taken_of_log_prob_percent: {}".format(
            #                         s.taken_of_log_prob_percent))
            # logger.info("taken_of_log_prob_percent_rank: {}".format(
            #                         s.taken_of_log_prob_percent_rank))
            # logger.info("similarities: {}".format([s.similarity_all_but,
            #                                        s.similarity_next,
            #                                        s.similarity_previous,
            #                                        s.similarity_last10,
            #                                        s.similarity_first10]))

        return top_sentences
