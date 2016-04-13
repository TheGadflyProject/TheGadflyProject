from .question import Question
from spacy.tokens.token import Token
from .q_generator_base import QGenerator, GapFillBlankType, QuestionType
import collections
import numpy
from random import shuffle


class MCQGenerator(QGenerator):

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

                    other_choices.append(ent.text_with_ws.strip())

                    shuffle(other_choices)

                    print("MCQ")
                    print(gap_fill_question)
                    print(ent)
                    print(other_choices)
                    print()

                    question = Question(sent_text, gap_fill_question,
                                        ent.text, QuestionType.gap_fill,
                                        GapFillBlankType.named_entities,
                                        set(other_choices))
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

        other_choices = [(span, sim) for span, sim in
                         other_choices if
                         entity.text_with_ws.strip() not in
                         span.text_with_ws.strip() and
                         span.text_with_ws not in sent.text_with_ws]
        other_choices = self.trim_choices(other_choices)
        other_choices = sorted(other_choices, key=lambda x: x[1], reverse=True)

        return [choice.text_with_ws.strip() for choice, sim in
                other_choices[:3]]

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
