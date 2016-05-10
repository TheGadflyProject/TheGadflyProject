from . import spacy_singleton
from .sentence_identifier import SentenceIdentifier
from .transducer import Transducer
from enum import Enum
import logging
import string
import collections
from random import shuffle
from . import nyt_popularity
from abc import ABC, abstractmethod
import json
logger = logging.getLogger("v.q_gen_b")


class QuestionType(Enum):
    gap_fill = "gap_fill"
    mcq = "mcq"


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return {"__enum__": str(obj)}
        return json.JSONEncoder.default(self, obj)

    def as_enum(d):
        if "__enum__" in d:
            name, member = d["__enum__"].split(".")
            return getattr(globals()[name], member)
        else:
            return d


class QGenerator(ABC):
    _GAP = " ___________ "
    _PUNCTUATION = list(string.punctuation)

    def __init__(self, source_text, q_limit=None):
        self.source_text = source_text
        self.parsed_text = spacy_singleton.spacy_en()(self.source_text)
        self.top_sents, self.sents = SentenceIdentifier(self.parsed_text,
                                                        n=50).sents()
        self._exclude_named_ent_types = ["DATE", "TIME", "PERCENT", "CARDINAL",
                                         "MONEY", "ORDINAL", "QUANTITY"]
        self.entities = self.find_named_entities()
        # self.transduced_sents = self.transduce(self.top_sents)
        self.questions = self.generate_questions()
        self.top_questions = self.select_top_question_for_sentence()
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

    @abstractmethod
    def generate_questions(self):
        """ implemented in subclass to gen questions"""

    def select_top_question_for_sentence(self):
        question_dict = collections.defaultdict(list)

        for q in self.questions:
            question_dict[q.source_sentence].append(q)

        final_questions = list()
        for source_sentence, questions in question_dict.items():
            ents = [question.answer for question in questions]
            try:
                most_popular = nyt_popularity.most_popular_terms(ents, 1)[0]
            except ValueError:
                shuffle(ents)
                most_popular = ents[:1]
            # hack to get around issues with NYT api throwing errors
            most_popular = most_popular or ents[:1]
            for question in questions:
                if question.answer == most_popular[0]:
                    final_questions.append(question)
                    break
        return final_questions

    def output_questions(self, questions=None, output_file=None):
        if questions is None:
            questions = self.top_questions

        questions = [vars(q) for n, q in enumerate(questions)]
        if output_file is not None:
            with output_file as o:
                json.dump(questions, o, cls=EnumEncoder)

        return questions
