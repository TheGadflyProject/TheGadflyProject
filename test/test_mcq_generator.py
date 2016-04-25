import unittest
from gadfly.mcq_generator import MCQGenerator, GapFillBlankType


class MCQGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.SOURCE_TEXT = """In the constant scorekeeping of where tech’s
        power centers are, two trends stand out in Asia: the continued rise of
        China as a tech titan and the slow decline of Japan’s once-mighty
        tech industry.

        Those currents were evident in two recent developments.

        On Thursday, Paul Mozur and Jane Perlez reported that American
        officials had blocked a proposed purchase of a controlling stake in a
        unit of the Dutch electronics company Philips by Chinese investors
        because the United States was fearful the deal would be used to
        further China’s push into microchips.

        At the center of the concerns was a material called gallium nitride,
        which was being used by the Philips unit in light-emitting diodes, but
        which has applications for military and space and can be helpful in
        semiconductors. The report illustrated how American officials have
        come to view China’s large and growing tech industry with misgivings.

        At the same time, Jonathan Soble and Paul Mozur reported that Sharp,
        one of Japan’s large consumer electronics companies and the biggest
        LCD producer, was leaning toward a takeover offer from the Taiwanese
        contract manufacturer Foxconn. The news underlined the decline of
        Japan’s once-famed consumer electronics companies, which have been
        undercut in recent years by lower-cost competition from China and
        South Korea."""
        self.mcq = MCQGenerator(self.SOURCE_TEXT,
                                [GapFillBlankType.named_entities],
                                )

    def test_output_to_list_should_return_list_not_set(self):
        self.assertIsInstance(self.mcq.output_questions_to_list(), list)

    def test_output_to_list_keys_should_include_required_fields(self):
        output_keys = set(self.mcq.output_questions_to_list()[0].keys())
        required_keys = set(["question", "answer", "answer_choices"])
        self.assertTrue(output_keys.issuperset(required_keys))

    def test_answer_choice_should_return_values(self):
        answer_choices = [s.answer_choices
                          for s in self.mcq.gen_named_entity_blanks()
                          if s.answer_choices is not None]
        self.assertTrue(answer_choices)

    def test_answer_choices_should_be_unique(self):
        answer_choices = [s.answer_choices
                          for s in self.mcq.gen_named_entity_blanks()
                          if s.answer_choices is not None]
        self.assertTrue(len(answer_choices[0]) == len(set(answer_choices[0])))

    def test_should_generate_zero_questions_with_no_named_ents(self):
        source_sentence =\
            "Those currents were evident in two recent developments."
        mcq = MCQGenerator(source_sentence,
                           [GapFillBlankType.named_entities],
                           )
        self.assertFalse(mcq.output_questions_to_list())

    def test_should_generate_one_question_with_one_named_ents(self):
        source_sentence =\
            "Those currents were evident in two recent developments " + \
            "in Iran."
        mcq = MCQGenerator(source_sentence,
                           [GapFillBlankType.named_entities],
                           )
        self.assertEqual(1, len(mcq.output_questions_to_list()))

    def test_should_generate_one_question_with_two_named_ents(self):
        source_sentence =\
            "Those NSA targets were evident in two recent developments " + \
            "in Iran."
        mcq = MCQGenerator(source_sentence,
                           [GapFillBlankType.named_entities],
                           )
        self.assertEqual(1, len(mcq.output_questions_to_list()))

    if __name__ == '__main__':
            unittest.main()
