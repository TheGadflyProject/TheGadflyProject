from . import spacy_singleton
from .sentence_summarizer import TF_IDFSummarizer
from .transducer import Transducer
from enum import Enum
import logging
import string
import types
import collections
from random import shuffle

logger = logging.getLogger("v.q_gen_b")


def tfidf(sents):
    selector = TF_IDFSummarizer(EDA=True)
    sents = [sent for sent in sents][1:]  # Issue #37
    # Issue  #39
    if sents[-1][0].orth_ == "(" and sents[-1][1].orth_ in ["Reporting",
                                                            "Writing"]:
            sents = sents[:-1]
    sentences = selector.summarize(sents, 5)
    return sentences


class QuestionType(Enum):
    gap_fill = "gap_fill"
    mcq = "mcq"


class GapFillBlankType(Enum):
    named_entities = "named_entities"
    noun_phrases = "noun_phrases"


class QGenerator:
    _GAP = " ___________ "
    _PUNCTUATION = list(string.punctuation)

    def __init__(self, source_text, gap_types, summarizer=None, q_limit=None):
        self._source_text = source_text
        self._parsed_text = spacy_singleton.spacy_en()(self._source_text)
        self.summarizer = types.MethodType(summarizer, self._parsed_text.sents)
        self._top_sents = self.summarizer()
        # self._top_sents = self.transduce(self._top_sents)
        self._gap_types = gap_types
        self._exclude_named_ent_types = ["DATE", "TIME", "PERCENT", "CARDINAL",
                                         "MONEY", "ORDINAL", "QUANTITY"]
        self.questions = self.generate_questions()
        self.q_limit = q_limit

    def transduce(self, sents):
        transduced_sents = [Transducer.transduce(sent) for sent in sents]
        return transduced_sents

    def find_named_entities(self):
        entities = []
        for ent in self._parsed_text.ents:
            if (ent.label_ != "" and
               ent.label_ not in self._exclude_named_ent_types):
                entities.append(ent)
        return entities

    def generate_questions(self):
        question_set = []
        for gap_type in self._gap_types:

            if gap_type == GapFillBlankType.named_entities:
                question_set += list(self.gen_named_entity_blanks())

            if gap_type == GapFillBlankType.noun_phrases:
                question_set += list(self.gen_noun_phrase_blanks())

            return question_set

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

    def question_selector(self):
        question_dict = collections.defaultdict(list)
        for q in self.questions:
            question_dict[q.source_sentence].append(q)

        final_questions = list()
        for source_sentence, questions in question_dict.items():
            shuffle(questions)
            final_questions.append(questions[0])

        return final_questions
