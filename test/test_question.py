import unittest
from gadfly.question import Question


class QuestionTest(unittest.TestCase):

    def setUp(self):
        self.source_sentence = "Daniel is the Gadfly."
        self.question = "______ is the Gadfly."
        self.answer = "Daniel"
        self.answer_span = None
        self.question_type = "GAP_FILL"

    def test_instanstiated_object_of_correct_type(self):
        q = Question(
            self.source_sentence,
            self.question,
            self.answer,
            self.answer_span,
            self.question_type,
        )
        self.assertIsInstance(q, Question)
    
    def test_should_equal(self):
        q1 = Question(
            self.source_sentence,
            self.question,
            self.answer,
            self.answer_span,
            self.question_type,
        )
        q2 = Question(
            self.source_sentence,
            self.question,
            self.answer,
            self.answer_span,
            self.question_type,
        )
        self.assertEqual(q1, q2)

if __name__ == '__main__':
    unittest.main()
