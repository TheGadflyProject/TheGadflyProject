from gadfly.question import Question
from gadfly.sentence_summarizer import FrequencySummarizer
from enum import Enum
import string
import re


class QuestionType(Enum):
    gap_fill = "GAP_FILL"


class GapFillBlankType(Enum):
    named_entities = "named_entities"


class GapFillGenerator:
    _GAP = "___________"
    _PUNCTUATION = list(string.punctuation)

    def __init__(self, parser, source_text, gap_types):
        self._source_text = source_text
        self._parsed_text = parser(self._source_text)
        self._most_important_sents = self.summarize_sentences()
        self._gap_types = gap_types
        self._exclude_named_ent_types = ["DATE",
                                         "TIME",
                                         "PERCENT",
                                         "CARDINAL",
                                         "MONEY",
                                         "ORDINAL",
                                         "QUANTITY"]
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
        for sent in self._most_important_sents:
            for entity in entities:
                # number of times entity found in sentence
                sent_ents = re.findall(entity, sent)
                if sent_ents:
                    for n in range(len(sent_ents)):
                        gap_fill_question = self._replaceNth(sent, entity, "_____", n)
                        question = Question(sent, gap_fill_question, entity, QuestionType.gap_fill)
                        named_entity_questions.add(question)

            return named_entity_questions

    def generate_questions(self):
        question_set = []
        for gap_type in self._gap_types:
            if gap_type == GapFillBlankType.named_entities:
                named_entity_questions = self.gen_named_entity_blanks()
                question_set += list(named_entity_questions)
            return set(question_set)

    def _replaceNth(self, sent, old, new, n):
        """Replaces the old with new at the nth index in sent
        Cite:inspectorG4dget http://stackoverflow.com/a/27589436"""
        inds = [i for i in range(len(sent) - len(old)+1)
                if sent[i:i+len(old)] == old]
        if len(inds) < n:
            return  # or maybe raise an error
        # can't assign to string slices. So, let's listify
        sent_list = list(sent)
        # do n-1 because we start from the first occurrence of the string,
        # not the 0-th
        sent_list[inds[n-1]:inds[n-1]+len(old)] = new
        return ''.join(sent_list)

    def output_questions_to_file(self, output_file):
        for n, q in enumerate(self.questions):
            output_file.write("\nQuestion #{}\n".format(n+1))
            output_file.write(
                ", ".join(["Q: {}".format(q.question),
                           "A: {}\n".format(q.answer)])
            )
        output_file.write("")
