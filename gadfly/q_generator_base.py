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
        self.source_text = source_text
        self.parsed_text = spacy_singleton.spacy_en()(self.source_text)
        self._identifier = types.MethodType(identifier, self.parsed_text.sents)
        self.sents = [sent for sent in self.parsed_text.sents]
        self.top_sents = self._identifier()
        self._exclude_named_ent_types = ["DATE", "TIME", "PERCENT", "CARDINAL",
                                         "MONEY", "ORDINAL", "QUANTITY"]
        self.entities = self.find_named_entities()
        # self.top_sents = self.transduce(self.top_sents)
        self.questions = self.generate_questions()
        self.top_questions = self.question_selector()
        self._q_limit = q_limit

    def transduce(self, sents):
        return [Transducer.transduce(sent) for sent in sents]

    def find_named_entities(self):
        entities = []
        for ent in self.parsed_text.ents:
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

    def output_questions(self, questions=None, output_file=None):
        if questions == None:
            questions = self.top_questions
        
        questions = [vars(q) for n, q in enumerate(questions)]        
        if output_file == None:
            with output_file as o:
                o.write("\n".join(questions))
                
        return questions

