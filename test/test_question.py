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
            self.source_sentence, self.question, self.answer,
            self.answer_span, self.question_type)
        self.assertIsInstance(q, Question)

    def test_should_equal(self):
        q1 = Question(
            self.source_sentence, self.question, self.answer,
            self.answer_span, self.question_type)
        q2 = Question(
            self.source_sentence, self.question, self.answer,
            self.answer_span, self.question_type)
        self.assertEqual(q1, q2)

    def test_should_not_equal(self):
        q1 = Question(
            self.source_sentence, self.question, self.answer,
            self.answer_span, self.question_type)
        q2 = Question(
            "This is just a test", self.question, self.answer,
            self.answer_span, self.question_type)
        self.assertNotEqual(q1, q2)

    def test_Mr_Trump_same_as_mr_trump(self):
        self.assertTrue(Question.is_correct_answer("Mr. Trump", "mr. trump"))

    def test_Mr_Trump_not_same_as_Hillary_Clinton(self):
        self.assertFalse(Question.is_correct_answer("Mr. Trump", "Hillary Clinton"))

    def test_Mr_Trump_is_same_as_Trump(self):
        self.assertTrue(Question.is_correct_answer("Mr. Trump", "Trump"))

    @unittest.skip("ideal for the future but skipping for now")
    def test_Mr_Trump_is_same_as_Donald_Trump(self):
        self.assertTrue(Question.is_correct_answer("Mr. Trump", "Donald Trump"))

if __name__ == '__main__':
    unittest.main()
