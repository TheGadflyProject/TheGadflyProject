from . import spacy_singleton
from .sentence_identifier import SentenceIdentifier
from .transducer import Transducer
from enum import Enum
import logging
import string
import types
import collections
from random import shuffle
from . import nyt_popularity
import abc
logger = logging.getLogger("v.q_gen_b")


def default_identifier(sents, n=5):
    selector = SentenceIdentifier(EDA=True)
    sents = [sent for sent in sents]  # Issue #37
    # Issue  #39
    if len(sents) < n:
        return sents
    elif len(sents) > 2:
        if sents[-1][0].orth_ == "(" and sents[-1][1].orth_ in ["Reporting",
                                                                "Writing"]:
            sents = sents[:-1]
    else:
        sents = sents[:-1]
    sentences = selector.identify(sents, n)
    return sentences


class QuestionType(Enum):
    gap_fill = "gap_fill"
    mcq = "mcq"


class QGenerator:
    _GAP = " ___________ "
    _PUNCTUATION = list(string.punctuation)

    def __init__(self, source_text,
                 identifier=default_identifier, q_limit=None):
        self._source_text = source_text
        self._parsed_text = spacy_singleton.spacy_en()(self._source_text)
        self.identifier = types.MethodType(identifier, self._parsed_text.sents)
        self._top_sents = self.identifier()
        # self._top_sents = self.transduce(self._top_sents)
        self._exclude_named_ent_types = ["DATE", "TIME", "PERCENT", "CARDINAL",
                                         "MONEY", "ORDINAL", "QUANTITY"]
        self.questions = self.generate_questions()
        self.q_limit = q_limit

    def get_sentences(self):
        return [sent for sent in self._parsed_text.sents]

    def transduce(self, sents):
        return [Transducer.transduce(sent) for sent in sents]

    def find_named_entities(self):
        entities = []
        for ent in self._parsed_text.ents:
            if (ent.label_ != "" and
               ent.label_ not in self._exclude_named_ent_types):
                entities.append(ent)
        return entities

    @abc.abstractmethod
    def generate_questions(self):
        """ implemented in subclass to gen questions"""

    def question_selector(self):
        question_dict = collections.defaultdict(list)
        for q in self.questions:
            question_dict[q.source_sentence].append(q)

        final_questions = list()
        for source_sentence, questions in question_dict.items():
            ents = [question.answer for question in questions]
            most_popular = nyt_popularity.most_popular_terms(ents, 1)[0]
            for question in questions:
                if question.answer == most_popular[0]:
                    final_questions.append(question)
                    break
        return final_questions

    def output_questions_to_list(self):
        questions = []
        for n, q in enumerate(self.question_selector()):
            questions.append(vars(q))
        return questions

    def output_questions_to_file(self, output_file):
        for n, q in enumerate(self.question_selector()):
            output_file.write("\nQuestion #{}\n".format(n+1))
            output_file.write(
                ", ".join(["Q: {}".format(q.question),
                           "Choices: {}".format(q.answer_choices),
                           "A: {}\n".format(q.answer)])
            )
        output_file.write("")

