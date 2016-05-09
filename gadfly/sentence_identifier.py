from collections import defaultdict
# from scipy.stats import rankdata
# import numpy
import logging
# from textstat.textstat import textstat

logger = logging.getLogger("v.sent_id")


class SentenceIdentifier:
    def __init__(self, parsed_text, n=10):
        sents = [sent for sent in parsed_text.sents]
        if len(sents) < n:
            logger.warn("Sentence count is {}, smaller than n({}).".format(
                        len(sents), n))
            n = len(sents)
        sents = self.repair_sents(parsed_text, sents)
        sent_objects = self.create_sent_objects(sents)

        ranked_sents_objects = self.get_ranked_sents(sent_objects)
        ranked_sents = [s.sent for s in ranked_sents_objects]
        self.top_sents = ranked_sents[:n]
        self.all_sents = [s.sent for s in sent_objects]

        # chosen_sents = [s for s in sent_objects if
        #                 s.has_named_entity]
        # for s in chosen_sents:
        #     print("#{}:\t{}".format(s.index, s.sent))

    def sents(self):
        return self.top_sents, self.all_sents

    def repair_sents(self, parsed_text, sents):
        sents = self.repair_joinedsents(parsed_text, sents)
        sents = self.repair_splitsents(parsed_text, sents)
        return sents

    def create_sent_objects(self, sents):
        sent_objects = [SentenceFeatures(sents, index) for index, sent
                        in enumerate(sents)]

        [s.set_log_probs() for s in sent_objects]
        article_object = ArticleFeatures(sent_objects)
        [s.set_ranks(article_object) for s in sent_objects]
        [s.set_score_ranking() for s in sent_objects]

        return sent_objects

    def check_joinedsents(self, parsed_text, sent):
        new_spans = []
        start1 = sent.start
        end1 = sent.start + [token.text_with_ws for token
                             in sent].index(". ") + 1
        start2 = end1
        end2 = sent.end
        if end1 != end2:
            if '. "' in "".join(token.text_with_ws for token in
                                parsed_text[start1:end1]):
                print(start1, end1, start2, end2)
                print(parsed_text[start1:end1])
                for each in self.check_joinedsents(parsed_text,
                                                   parsed_text[start1:end1]):
                    new_spans.append(each)
            else:
                return [sent]
        else:
            new_spans.append(parsed_text[start1:end1])
        if '. "' in "".join(token.text_with_ws for token in
                            parsed_text[start2:end2]):
            for each in self.check_joinedsents(parsed_text,
                                               parsed_text[start2:end2]):
                new_spans.append(each)
        else:
            new_spans.append(parsed_text[start2:end2])
        return new_spans

    def repair_joinedsents(self, parsed_text, sents):
        new_spans = []
        for index, sent in enumerate(sents):
            if '. "' in "".join(token.text_with_ws for token in sent[:-2]):
                for each in self.check_joinedsents(parsed_text, sent):
                    new_spans.append(each)
            else:
                new_spans.append(sent)
        return new_spans

    def repair_splitsents(self, parsed_text, sents):
        outer_check = 0
        new_spans = []
        while True:
            if outer_check >= len(sents):
                break
            s = sents[outer_check]
            quote_tokens = [token for token in s if token.orth_ == '"']
            if bool(len(quote_tokens) & 1):
                inner_check = outer_check + 1
                start = s.start
                while True:
                    if inner_check == len(sents):
                        new_spans.append(parsed_text[
                            sents[outer_check].start:sents[outer_check].end])
                        outer_check += 1
                        logger.warn("QUOTATION UNMATCHED: index={}".format(
                                                                outer_check))
                        break
                    if sents[inner_check][-1].orth_.strip() == '"':
                        end = sents[inner_check].end
                        outer_check += (inner_check - outer_check + 1)
                        break
                    else:
                        quote_tokens = [token for token in sents[inner_check]
                                        if token.orth_.strip() == '"']
                        if bool(len(quote_tokens) & 1):
                            end = sents[inner_check].end
                            outer_check += (inner_check - outer_check + 1)
                            break
                        else:
                            inner_check += 1
                new_spans.append(parsed_text[start:end])
            else:
                new_spans.append(s)
                outer_check += 1
        return new_spans

    def get_ranked_sents(self, sent_objects):
        ranked_sents = list()
        for s in sent_objects:
            if s.score_ranking:
                ranked_sents.append((s.score_ranking, s))
        return [s for rank, s in sorted(ranked_sents)]


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
        # self.char_count = len(str(self.sent))
        # self.char_count_rank = None
        # self.token_count = len(self.sent)
        # self.token_count_rank = None
        self.log_prob_list = list()
        self.total_log_prob = 0
        # self.total_log_prob_rank = None
        # self.taken_log_prob = 0
        # self.taken_log_prob_rank = None
        # self.taken_of_total_log_prob_percent = None
        # self.taken_of_log_prob_percent = 0
        # self.taken_of_log_prob_percent_rank = None
        self.ent_types_count = defaultdict(int)
        # self.out_of_vocab_list = list()
        # self.low_log_prob_list = list()
        # self.low_log_prob_count_rank = None
        self.ent_count = 0
        # self.ent_count_rank = None

        self.has_named_entity = self.set_has_named_entity()

        # self.smog_index = textstat.smog_index(self.text)
        # self.syllable_count = textstat.syllable_count(self.text)
        # self.gunning_fog = textstat.gunning_fog(self.text)
        # self.linsear_write_formula = textstat.linsear_write_formula(
        #                             self.text)
        # self.coleman_liau_index = textstat.coleman_liau_index(self.text)
        # self.automated_readability_index = textstat.\
        #     automated_readability_index(self.text)

        # if len(self.article) >= 20:
        #     cutoff = 10
        # else:
        #     cutoff = int(len(self.article)/2)
        # self.similarity_first10 = numpy.mean([self.sent.similarity(sent) for
        #                                       index, sent in enumerate(
        #                                       self.article[:cutoff]) if index
        #                                       is not self.index])
        # self.similarity_last10 = numpy.mean([self.sent.similarity(sent) for
        #                                      index, sent in enumerate(
        #                                      self.article[-cutoff:]) if index
        #                                      is not self.index])
        # if self.index == 0:
        #     self.similarity_previous = None
        # else:
        #     self.similarity_previous = self.sent.similarity(
        #                                     self.article[self.index-1])
        # if self.index + 1 == len(self.article):
        #     self.similarity_next = 0
        # else:
        #     self.similarity_next = self.sent.similarity(self.article[
        #                                     self.index+1])
        # self.similarity_all_but = numpy.mean([self.sent.similarity(sent) for
        #                                       index, sent in enumerate(
        #                                       self.article) if index is
        #                                       not self.index])

    def set_ranks(self, article_object):
        self.index_rank = self.index / len(self.article)
        # self.char_count_rank = list(
        #     rankdata(article_object.char_counts))[self.index] /\
        #     len(self.article)
        # self.token_count_rank = list(
        #     rankdata(article_object.char_counts))[self.index] /\
        #     len(self.article)
        # self.total_log_prob_rank = list(
        #     rankdata(article_object.total_log_probs))[self.index] /\
        #     len(self.article)
        # self.taken_log_prob_rank = list(
        #     rankdata(article_object.taken_log_probs))[self.index] /\
        #     len(self.article)
        # self.low_log_prob_count_rank = list(
        #     rankdata(article_object.low_log_prob_counts))[self.index] /\
        #     len(self.article)
        # self.ent_count_rank = list(
        #     rankdata(article_object.ent_counts))[self.index] /\
        #     len(self.article)
        # self.taken_of_log_prob_percent_rank = list(
        #     rankdata(article_object.taken_of_log_prob_percents))[
        #              self.index] / len(self.article)

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
                # self.out_of_vocab_list.append(token)
                continue
            elif log_prob < -15:
                pass
                # self.low_log_prob_list.append((token, log_prob))
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
        pass
        # self.char_counts = [s.char_count for s in sent_objects]
        # self.token_counts = [s.token_count for s in sent_objects]
        # self.total_log_probs = [s.total_log_prob for s in sent_objects]
        # self.taken_log_probs = [s.taken_log_prob for s in sent_objects]
        # self.low_log_prob_counts = [len(s.low_log_prob_list) for s in
        #                             sent_objects]
        # self.ent_counts = [s.ent_count for s in sent_objects]

        # self.has_named_entity_list = [True if s.has_named_entity
        #                               else False for s in sent_objects]
        # self.has_named_entity_count = sum(self.has_named_entity_list)
        # self.taken_of_log_prob_percents = [s.taken_of_log_prob_percent
        #                                    for s in sent_objects]
