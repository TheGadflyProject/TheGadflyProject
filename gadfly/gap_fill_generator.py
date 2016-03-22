from gadfly import spacy_singleton
from gadfly.question import Question
from gadfly.sentence_summarizer import FrequencySummarizer
from gadfly.utilities import replaceNth
from gadfly.transducer import Transducer
from enum import Enum
from itertools import product
import string
import re


class QuestionType(Enum):
    gap_fill = "gap_fill"


class GapFillBlankType(Enum):
    named_entities = "named_entities"
    noun_phrases = "noun_phrases"


class GapFillGenerator:
    _GAP = "___________"
    _PUNCTUATION = list(string.punctuation)

    def __init__(self, source_text, gap_types):
        self._source_text = source_text
        self._parsed_text = spacy_singleton.spacy_en()(self._source_text)
        self._most_important_sents = self.summarize_sentences()
        # self._transduced_sents = Transducer.transduce(self._most_important_sents)
        self._gap_types = gap_types
        self._exclude_named_ent_types = ["DATE", "TIME", "PERCENT", "CARDINAL",
                                         "MONEY", "ORDINAL", "QUANTITY"]
        self.questions = self.generate_questions()

    def summarize_sentences(self):
        fs = FrequencySummarizer()
        sents = []
        for span in self._parsed_text.sents:
            sent = [self._parsed_text[i] for i in range(span.start, span.end)]
            tokens = []
            for token in sent:
                tokens.append(token.text)
            sents.append(tokens)
        sentences = fs.summarize(sents, 5)
        return sentences

    def find_named_entities(self):
        entities = set()
        for ent in self._parsed_text.ents:
            if (ent.label_ != "" and
               ent.label_ not in self._exclude_named_ent_types):
                entities.add(ent.text_with_ws)
        return entities

    def gen_named_entity_blanks(self):
        named_entity_questions = set()
        entities = self.find_named_entities()
        for sent, entity in product(self._most_important_sents, entities):
            # number of times entity found in sentence
            sent_ents = re.findall(entity, sent)
            if sent_ents:
                for n in range(len(sent_ents)):
                    gap_fill_question = replaceNth(sent, entity, "_____", n)
                    question = Question(sent, gap_fill_question, entity,
                                        QuestionType.gap_fill,
                                        GapFillBlankType.named_entities)
                    named_entity_questions.add(question)

        return named_entity_questions

    def gen_noun_phrase_blanks(self):
        noun_phrase_questions = set()
        noun_phrases = [np.text for np in self._parsed_text.noun_chunks]
        for sent, np in product(self._most_important_sents, noun_phrases):
            sent_nps = re.findall(np, sent)
            if sent_nps:
                for n in range(len(sent_nps)):
                    gap_fill_question = replaceNth(sent, np, "_____", n)
                    question = Question(sent, gap_fill_question, np,
                                        QuestionType.gap_fill,
                                        GapFillBlankType.noun_phrases)
                    noun_phrase_questions.add(question)

        return noun_phrase_questions

    def generate_questions(self):
        question_set = []
        for gap_type in self._gap_types:

            if gap_type == GapFillBlankType.named_entities:
                question_set += list(self.gen_named_entity_blanks())

            if gap_type == GapFillBlankType.noun_phrases:
                question_set += list(self.gen_noun_phrase_blanks())

            return set(question_set)

    def output_questions_to_file(self, output_file):
        for n, q in enumerate(self.questions):
            output_file.write("\nQuestion #{}\n".format(n+1))
            output_file.write(
                ", ".join(["Q: {}".format(q.question),
                           "A: {}\n".format(q.answer)])
            )
        output_file.write("")
