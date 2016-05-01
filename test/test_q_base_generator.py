import unittest
from gadfly.q_generator_base import QGenerator


class QGeneratorTest(unittest.TestCase):

    def test_base_class_cannot_be_instantiated(self):
        source_sentence =\
            "Those NSA targets were evident in two recent developments " + \
            "in Iran."
        self.assertRaises(TypeError, lambda: QGenerator(source_sentence))

    if __name__ == '__main__':
            unittest.main()
