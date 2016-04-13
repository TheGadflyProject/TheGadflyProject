from . import spacy_singleton
from .question import Question
from .sentence_summarizer import TF_IDFSummarizer
from .transducer import Transducer
from spacy.tokens.token import Token
from enum import Enum
import string
import types
import collections
import numpy


def tfidf(self):
    selector = TF_IDFSummarizer(EDA=True)
    sents = [sent for sent in self._parsed_text.sents]
    sentences = selector.summarize(sents, 5)
    print("New Article:\n")
    for n, sent in enumerate(sentences):
        print("Sent {}, sent length:{}".format(n, len(sent)))
        print(sent)
    print()
    return sentences


class QuestionType(Enum):
    gap_fill = "gap_fill"


class GapFillBlankType(Enum):
    named_entities = "named_entities"
    noun_phrases = "noun_phrases"


class GapFillGenerator:
    _GAP = " ___________ "
    _PUNCTUATION = list(string.punctuation)

    def __init__(self, source_text, gap_types, summarizer=None):
        self._source_text = source_text
        self._parsed_text = spacy_singleton.spacy_en()(self._source_text)
        self.summarizer = types.MethodType(summarizer, self)
        self._top_sents = self.summarizer()
        # self._top_sents = self.transduce(self._top_sents)
        self._gap_types = gap_types
        self._exclude_named_ent_types = ["DATE", "TIME", "PERCENT", "CARDINAL",
                                         "MONEY", "ORDINAL", "QUANTITY"]
        self.questions = self.generate_questions()

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

    def gen_named_entity_blanks(self):
        named_entity_questions = []
        entities_dict = self.build_entities_dictionary()
        print(entities_dict)
        entities = self.find_named_entities()
        for sent in self._top_sents:
            sent_text = "".join(
                    [t.text_with_ws if type(t) == Token else t for t in sent])
            for ent in entities:
                if (sent.start < ent.start and sent.end > ent.end):
                    gap_fill_question = str(self._parsed_text[
                                            sent.start:ent.start]) \
                                        + self._GAP + str(self._parsed_text[
                                                          ent.end:sent.end])
                    other_choices = self.generate_other_choices(entities_dict,
                                                                ent, sent)
                    print("MCQ")
                    print(gap_fill_question)
                    print(ent)
                    print(other_choices)
                    print()

                    question = Question(sent_text, gap_fill_question,
                                        ent.text, QuestionType.gap_fill,
                                        GapFillBlankType.named_entities)
                    named_entity_questions.append(question)
        return named_entity_questions

    def generate_other_choices(self, entities_dict, entity, sent):
        all_entities = entities_dict[entity.label_]
        other_choices = [(ent,
                          str(numpy.round(numpy.array(
                                          [ent.similarity(entity)]),
                                          3))
                          ) for ent in all_entities]
        # remove choices that are already in the sentence

        other_choices = [(span, sim) for span, sim in other_choices if
                         entity.text_with_ws.strip() not in
                         span.text_with_ws.strip() and
                         span.text_with_ws not in sent.text_with_ws]
        other_choices = self.trim_choices(other_choices)
        other_choices = sorted(other_choices, key=lambda x: x[1], reverse=True)
        return other_choices[:3]

    def build_entities_dictionary(self):
        entities_dict = collections.defaultdict(list)
        entities = self.find_named_entities()
        for entity in entities:
            if entity.text_with_ws.strip() not in [e.text_with_ws.strip()
               for e in entities_dict[entity.label_]]:
                    entities_dict[entity.label_].append(entity)
        return entities_dict

    def trim_choices(self, other_choices):
        ents = [word.text_with_ws.strip() for word, sim in other_choices]
        ents = sorted(ents, key=len)
        keep_list = []
        i = 0
        while i < len(ents):
            j = i+1
            kill = False
            while j < len(ents):
                if ents[i] in ents[j]:
                    kill = True
                    break
                j += 1
            if kill is False:
                keep_list.append(ents[i])
            i += 1
        ents = [(ent, sim) for ent, sim in other_choices
                if ent.text_with_ws.strip() in keep_list]
        return ents

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
        for n, q in enumerate(self.questions):
            questions.append(vars(q))
        return questions

    def output_questions_to_file(self, output_file):
        for n, q in enumerate(self.questions):
            output_file.write("\nQuestion #{}\n".format(n+1))
            output_file.write(
                ", ".join(["Q: {}".format(q.question),
                           "A: {}\n".format(q.answer)])
            )
        output_file.write("")
