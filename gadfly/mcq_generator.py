from .question import Question
from spacy.tokens.token import Token
from .q_generator_base import QGenerator, QuestionType
from .heuristic_evaluator import HeuristicEvaluator
import logging
from random import shuffle
from . import nyt_popularity
import collections
import numpy
import pickle
from random import shuffle

logger = logging.getLogger("v.mcq_g")


class MCQGenerator(QGenerator):

    def generate_question(self, sent_start, sent_end):
        entities_dict = self.build_entities_dictionary()
        entities = self.entities
        sent = self.parsed_text[sent_start:sent_end]
        sent_text = "".join(
                [t.text_with_ws if type(t) == Token else t for t in sent])
        for ent in entities:
            ent_text = ent.text_with_ws.strip()
            if (sent_start <= ent.start and sent_end >= ent.end):
                # if 's in entity, then ent_end will reduce by 1 and
                # ent_text will have no '
                # ent_end, ent_text = ent.end, ent.text_with_ws
                ent_end, ent_text = HeuristicEvaluator.remove_apos_s_ans(
                                        ent, self.parsed_text)
                gap_fill_question = str(
                        self.parsed_text[sent_start:ent.start]) + \
                    self._GAP + \
                    str(self.parsed_text[ent_end:sent_end])
                other_choices = self.generate_other_choices(entities_dict,
                                                            ent, sent)
                # Heuristic: handles the case when titles maybe present in
                # a sentence. We change all the options to only last name.
                other_choices = HeuristicEvaluator.check_titles(
                    ent, gap_fill_question, other_choices)
                # Reduce no. of choices to 3
                other_choices = other_choices[:3]
                # Heuristic evaluator - remove apostrophes
                other_choices = HeuristicEvaluator.remove_apos_s_choices(
                    other_choices)

                if ent.label_ == "GPE":
                    ent_text, other_choices = HeuristicEvaluator.\
                        gpe_evaluator(other_choices, ent_text)

                # No. of choices now becomes 4
                other_choices.append(ent_text)
                # Randomize choices
                shuffle(other_choices)

                logger.debug("Question:")
                logger.debug(str(gap_fill_question))
                logger.debug(str(ent.label_))
                logger.debug("ent_text: {}".format(str(ent_text)))
                logger.debug("answer_choices: {}".format(
                    str(other_choices)))

                question = Question(sent_text, gap_fill_question,
                                    ent_text, ent, QuestionType.mcq,
                                    ["named_entities"],
                                    list(set(other_choices)))
                return question

    def generate_questions(self):
        return [self.generate_question(sent.start, sent.end) 
                for sent in self.top_sents
                if self.generate_question(sent.start, sent.end) != None]

    def generate_other_choices(self, entities_dict, entity, sent):
        all_entities = entities_dict[entity.label_]
        other_choices = [(ent,
                          str(numpy.round(numpy.array(
                                          [ent.similarity(entity)]),
                                          3))
                          ) for ent in all_entities]
        # remove choices that are already in the sentence
        # remove choices that maybe contained within the answer
        # remove choices that the answer is in
        other_choices = [(span, sim) for span, sim in
                         other_choices if
                         entity.text_with_ws.strip() not in
                         span.text_with_ws.strip() and
                         span.text_with_ws.strip() not in sent.text_with_ws and
                         span.text_with_ws.strip() not in
                         entity.text_with_ws.strip()]
        # remove choices where it is present within another choice
        other_choices = self.trim_choices(other_choices)
        # sorting by similarity
        other_choices = sorted(other_choices, key=lambda x: x[1], reverse=True)
        # returning list of text choices (from spans)
        return [choice.text_with_ws.strip() for choice, sim in
                other_choices]

    def build_entities_dictionary(self):
        entities_dict = collections.defaultdict(list)
        entities = self.find_named_entities()
        for entity in entities:
            if entity.start == 0 and entity.text_with_ws.strip().isupper():
                continue
            if entity.text_with_ws.strip() not in [e.text_with_ws.strip()
               for e in entities_dict[entity.label_]]:
                    entities_dict[entity.label_].append(entity)
        return entities_dict

    def trim_choices(self, other_choices):
        '''
            This handles one option being within another.
            Ex: Bush, George Bush cannot be 2 options for the same question.
        '''
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

    def select_top_question_for_sentence(self):
        question_dict = collections.defaultdict(list)

        for q in self.questions:
            if len(q.answer_choices) == 4:
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
        return [q for q in final_questions][:10]
