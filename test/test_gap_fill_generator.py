import unittest
from gadfly.source_text import SourceText
from gadfly.gap_fill_generator import GapFillGenerator


class GapFillGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.source_text = SourceText('./news_articles/China Is Rising.txt')

    def test_instanstiated_object_of_correct_type(self):
        gfg = GapFillGenerator(self.source_text)
        self.assertIsInstance(gfg, GapFillGenerator)

if __name__ == '__main__':
    unittest.main()
