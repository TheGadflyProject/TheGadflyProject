import unittest
from gadfly.heuristic_evaluator import HeuristicEvaluator
from gadfly.gap_fill_generator import GapFillGenerator


class HeuristicEvaluatorTest(unittest.TestCase):

    def setUp(self):
        self.SOURCE_TEXT = """
        At the same time, Jonathan Soble and Paul Mozur reported that Sharp,
        one of Japan’s large consumer electronics companies and the biggest
        LCD producer, was leaning toward a takeover offer from the Taiwanese
        contract manufacturer Foxconn."""
        self.gfg = GapFillGenerator(self.SOURCE_TEXT)

    def test_name_titles_should_be_removed(self):
        source_text = """
        At the same time, Mr. Jonathan Soble and Mr. Paul Mozur reported something
        """
        pass


if __name__ == '__main__':
    unittest.main()
