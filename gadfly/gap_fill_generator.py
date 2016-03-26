from gadfly import spacy_singleton
from gadfly.question import Question
from gadfly.sentence_summarizer import FrequencySummarizer
from gadfly.utilities import replaceNth
from gadfly.utilities import is_left_child
from gadfly.transducer import Transducer
from spacy.tokens.token import Token
from enum import Enum
from itertools import product
import string
import re


class QuestionType(Enum):
    gap_fill = "gap_fill"
    wh_questions = "wh_questions"


class GapFillBlankType(Enum):
    named_entities = "named_entities"
    noun_phrases = "noun_phrases"


class QuestionPhrases(Enum):
    who = "Who "
    what = "What "
    where = "Where "


class GapFillGenerator:
    _GAP = "___________ "
    _PUNCTUATION = list(string.punctuation)

    def __init__(
            self,
            source_text,
            gap_types,
            question_type=QuestionType.gap_fill
            ):
        self._source_text = source_text
        self._parsed_text = spacy_singleton.spacy_en()(self._source_text)
        self._top_short_sents = self.summarize_sentences()
        self._top_sent_tuples = self.transduce(self._top_short_sents)
        self._top_sents = self.get_top_sentences(self._top_sent_tuples)
        self._gap_types = gap_types
        self._exclude_named_ent_types = ["DATE", "TIME", "PERCENT", "CARDINAL",
                                         "MONEY", "ORDINAL", "QUANTITY"]
        self.questions = self.generate_questions(question_type)

    def transduce(self, sents):
        transduced_sents = [
            (Transducer.transduce(sent), sent) for sent in sents]
        return transduced_sents

    def get_top_sentences(self, sent_tuples):
        top_sents = [str_sent for str_sent, spacy_sent in sent_tuples]
        return top_sents

    def summarize_sentences(self):
        fs = FrequencySummarizer()
        sentences = fs.summarize(self._parsed_text, 5)
        return sentences

    def find_named_entities(self):
        entities = set()
        for ent in self._parsed_text.ents:
            if (ent.label_ != "" and
               ent.label_ not in self._exclude_named_ent_types):
                entities.add(ent.text_with_ws)
        return entities

    def find_named_entity_tuples(self):
        # not sure if list is important
        # if it is, __hash__ needs to be implemented
        entities = list()
        for ent in self._parsed_text.ents:
            if (ent.label_ != "" and
               ent.label_ not in self._exclude_named_ent_types):
                entities.append((ent.text_with_ws, ent))
        return entities

    def gen_named_entity_blanks(self):
        named_entity_questions = set()
        entities = self.find_named_entities()
        for sent, entity in product(self._top_sents, entities):
            # number of times entity found in sentence
            sent_text = "".join(
                [t.text_with_ws if type(t) == Token else t for t in sent])
            sent_ents = re.findall(entity, sent_text)
            if sent_ents:
                for n in range(len(sent_ents)):
                    gap_fill_question = replaceNth(sent_text, entity,
                                                   self._GAP, n)
                    question = Question(sent_text, gap_fill_question, entity,
                                        QuestionType.gap_fill,
                                        GapFillBlankType.named_entities)
                    named_entity_questions.add(question)

        return named_entity_questions

    def gen_noun_phrase_blanks(self):
        noun_phrase_questions = set()
        noun_phrases = [np.text for np in self._parsed_text.noun_chunks]
        for sent, np in product(self._top_sents, noun_phrases):
            sent_text = "".join(
                [t.text_with_ws if type(t) == Token else t for t in sent])
            sent_nps = re.findall(np, sent_text)
            if sent_nps:
                for n in range(len(sent_nps)):
                    gap_fill_question = replaceNth(sent_text, np, self._GAP, n)
                    question = Question(sent_text, gap_fill_question, np,
                                        QuestionType.gap_fill,
                                        GapFillBlankType.noun_phrases)
                    noun_phrase_questions.add(question)

        return noun_phrase_questions

    def gen_correct_question_phrase(self, entity):
        if entity.label_ in ["NOPR", "PERSON", "ORG", "FACILITY"]:
            return QuestionPhrases.who.value
        elif entity.label_ in ["GPE", "LOC"]:
            return QuestionPhrases.where.value
        else:
            return QuestionPhrases.what.value

    def is_aux_there(self, parsed_sent):
        root_token = Transducer.get_root_token(parsed_sent)
        tokens_before_root = []
        # identify tokens before root
        for token in parsed_sent:
            if type(token) == str:
                continue
            if token != root_token:
                tokens_before_root.append(token)
            else:
                # reached root token
                break
        # is there an auxiliary verb?
        for token in tokens_before_root:
            if token.dep_ == "aux":
                return (True, token)
        return (False, None)

    def transform(self, parsed_sent, simplified_text, answer, n):
        root_token = Transducer.get_root_token(parsed_sent)
        # 1. Is the answer in the left subtree
        if is_left_child(
                simplified_text, root_token, answer) == True:
            # 1.a. Replace answer with QP
            wh_question = replaceNth(
                simplified_text,
                answer.text_with_ws,
                self.gen_correct_question_phrase(answer),
                n)
        else:
            # 2. Check if there is an aux verb
            flag, token = self.is_aux_there(parsed_sent)
            if flag:
                # 2.a Get correct QP
                QP = self.gen_correct_question_phrase(answer)
                # 2.b Combine QP with aux verb
                QP = QP + token.text_with_ws + " "
                # 2.c Remove exiting aux verb
                wh_question = simplified_text.replace(token.text_with_ws, "")
                # 2.d Combine QP with sentence
                wh_question = QP + wh_question
                # 2.e Remove Answer
                wh_question = wh_question.replace(answer.text_with_ws, "")
            else:
                QP = self.gen_correct_question_phrase(answer)
                QP = QP + "did "
                wh_question = simplified_text.replace(answer.text_with_ws, "")
                wh_question = wh_question.replace(
                        root_token.text_with_ws, root_token.lemma_+" ")
                wh_question = QP + wh_question
        return wh_question

    def gen_wh_questions(self):
        wh_questions = set()
        entities = self.find_named_entity_tuples()
        for (simplified_text, spacy_sent), (e_str, e) in product(
                self._top_sent_tuples, entities):
            simplified_text = "".join(
                [t.text_with_ws
                 if type(t) == Token else t for t in simplified_text])
            # print(simplified_text, spacy_sent, e_str, e)
            # print("Type check: ", type(e_str), type(simplified_text))
            sent_ents = re.findall(e_str, simplified_text)
            if sent_ents:
                for n in range(len(sent_ents)):
                    # n is only to be able to re-use ReplaceNth method
                    wh_question = self.transform(
                        spacy_sent, simplified_text, e, n)
                    # what is gap fill blank type- 5th param with default value
                    question = Question(
                        simplified_text,
                        wh_question,
                        e.text_with_ws,
                        QuestionType.wh_questions)
                    # TBD: post_processing(wh_question) - convert . into ?
                    wh_questions.add(question)
        return wh_questions

    def generate_questions(self, question_type):
        question_set = []
        if question_type == QuestionType.gap_fill:
            for gap_type in self._gap_types:

                if gap_type == GapFillBlankType.named_entities:
                    question_set += list(self.gen_named_entity_blanks())

                if gap_type == GapFillBlankType.noun_phrases:
                    question_set += list(self.gen_noun_phrase_blanks())

        elif question_type == QuestionType.wh_questions:
            question_set += list(self.gen_wh_questions())
        # This could be a bug. Moving it outside the loop.
        return set(question_set)

    def output_questions_to_file(self, output_file):
        for n, q in enumerate(self.questions):
            output_file.write("\nQuestion #{}\n".format(n+1))
            output_file.write(
                ", ".join(["Q: {}".format(q.question),
                           "A: {}\n".format(q.answer)])
            )
        output_file.write("")
