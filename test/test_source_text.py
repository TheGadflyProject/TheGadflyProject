import unittest
from gadfly.source_text import SourceText


class SourceTextTest(unittest.TestCase):

    def test_instanstiated_object_of_correct_type(self):
        st = SourceText('./news_articles/China Is Rising.txt')
        self.assertIsInstance(st, SourceText)

if __name__ == '__main__':
    unittest.main()
