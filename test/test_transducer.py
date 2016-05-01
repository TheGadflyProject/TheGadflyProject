import unittest
from gadfly import spacy_singleton
from gadfly.transducer import Transducer
from spacy.tokens.token import Token


class TransducerTest(unittest.TestCase):

    def test_transuder_returns_expected_putin_sentence(self):
        sent = """Prime Minister Putin, country's paramount leader, cut short a trip to Siberia."""
        correct_output = "Prime Minister Putin cut short a trip to Siberia."
        parsed = spacy_singleton.spacy_en()(sent)
        transduced = Transducer.transduce(parsed)
        transduced = "".join(
            [t.text_with_ws if type(t) == Token else t for t in transduced])
        return self.assertEqual(transduced, correct_output)
        
    def test_transuder_returns_expected_sentence(self):
        sent = """Johnathan Wilson, a shy man, replaced his position in the dark."""
        correct_output = "Johnathan Wilsonreplaced his position in the dark."
        parsed = spacy_singleton.spacy_en()(sent)
        transduced = Transducer.transduce(parsed)
        transduced = "".join(
            [t.text_with_ws if type(t) == Token else t for t in transduced])
        return self.assertEqual(transduced, correct_output)

if __name__ == '__main__':
    unittest.main()
