from .question import Question
from spacy.tokens.token import Token
from .q_generator_base import QGenerator, GapFillBlankType, QuestionType
from .heuristic_evaluator import HeuristicEvaluator
import logging
import collections
import numpy
from random import shuffle

logger = logging.getLogger("v.mcq_g")


class MCQGenerator(QGenerator):

    def gen_named_entity_blanks(self):
        named_entity_questions = []
        entities_dict = self.build_entities_dictionary()
        # print(entities_dict)
        # for span in self._parsed_text:
        #     print(span, span.pos_)
        entities = self.find_named_entities()
        for sent in self._top_sents:
            sent_text = "".join(
                    [t.text_with_ws if type(t) == Token else t for t in sent])
            for ent in entities:
                ent_text = ent.text_with_ws.strip()
                if (sent.start < ent.start and sent.end > ent.end):
                    # if 's in entity, then ent_end will reduce by 1 and
                    # ent_text will have no '
                    # ent_end, ent_text = ent.end, ent.text_with_ws
                    ent_end, ent_text = HeuristicEvaluator.remove_apos_s_ans(
                        ent, self._parsed_text)
                    gap_fill_question = str(self._parsed_text
                                            [sent.start:ent.start]) \
                        + self._GAP + str(self._parsed_text[ent_end:sent.end])
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
                    # No. of choices now becomes 4
                    other_choices.append(ent_text)
                    # Randomize choices
                    shuffle(other_choices)

                    logger.debug("Question:")
                    logger.debug(str(gap_fill_question))
                    logger.debug(str(ent.label_))
                    logger.debug("ent_text: {}".format(str(ent_text)))
                    logger.debug("other_choices: {}".format(
                        str(other_choices)))

                    # print("#"*30)

                    question = Question(sent_text, gap_fill_question,
                                        ent_text, ent, QuestionType.mcq,
                                        GapFillBlankType.named_entities,
                                        set(other_choices))
                    named_entity_questions.append(question)
        # print("#"*80)
        return named_entity_questions

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
