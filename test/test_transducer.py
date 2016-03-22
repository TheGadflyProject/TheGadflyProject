import unittest

from gadfly import spacy_singleton
from gadfly.transducer import Transducer


class TransducerTest(unittest.TestCase):

    def test_instanstiated_object_of_correct_type(self):
        sent = """Prime Minister Putin, country's paramount leader, cut short a trip to Siberia."""
        correct_output = "Prime Minister Putin cut short a trip to Siberia"
        parsed = spacy_singleton.spacy_en()(sent)
        return self.assertEqual(Transducer.transduce(parsed), correct_output)

if __name__ == '__main__':
    unittest.main()
