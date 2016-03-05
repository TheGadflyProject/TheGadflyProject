import unittest
from gadfly.question import Question


class QuestionTest(unittest.TestCase):

    def setUp(self):
        self.source_sentence = "Daniel is the Gadfly."
        self.gap_fill_sentence = "______ is the Gadfly."
        self.answer = "Daniel"
        self.question_type = "GAP_FILL"

    def test_instanstiated_object_of_correct_type(self):
        q = Question(
            self.source_sentence,
            self.gap_fill_sentence,
            self.answer,
            self.question_type,
        )
        self.assertIsInstance(q, Question)

if __name__ == '__main__':
    unittest.main()
