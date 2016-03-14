import unittest
from gadfly.grammar_utilities import Chunker


class ChunkerTest(unittest.TestCase):

    def test_instanstiated_object_of_correct_type(self):
        chunker = Chunker()
        self.assertIsInstance(chunker, Chunker)

if __name__ == '__main__':
    unittest.main()
