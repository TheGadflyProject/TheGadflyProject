from .question import Question
from spacy.tokens.token import Token
from .q_generator_base import QGenerator, QuestionType


class GapFillGenerator(QGenerator):

    def generate_questions(self):
        named_entity_questions = []
        entities = self.find_named_entities()
        for sent in self.top_sents:
            sent_text = "".join(
                    [t.text_with_ws if type(t) == Token else t for t in sent])
            for ent in entities:
                if (sent.start < ent.start and sent.end > ent.end):
                    gap_fill_question = str(self.parsed_text[
                                            sent.start:ent.start]) \
                                        + self._GAP + str(self.parsed_text[
                                                          ent.end:sent.end])

                    question = Question(sent_text, gap_fill_question,
                                        ent.text, ent, QuestionType.gap_fill,
                                        "named_entities")
                    named_entity_questions.append(question)
        return named_entity_questions
