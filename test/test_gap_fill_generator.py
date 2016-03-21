import unittest
from gadfly.gap_fill_generator import GapFillGenerator, GapFillBlankType
from spacy.en import English


class GapFillBlankTypeTest(unittest.TestCase):
    def test_instanstiated_object_of_correct_type(self):
        q_type_named_entity = GapFillBlankType.named_entities
        self.assertIsInstance(q_type_named_entity, GapFillBlankType)


class GapFillGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.SOURCE_TEXT = """In the constant scorekeeping of where tech’s
        power centers are, two trends stand out in Asia: the continued rise of
        China as a tech titan and the slow decline of Japan’s once-mighty
        tech industry.

        Those currents were evident in two recent developments.

        On Thursday, Paul Mozur and Jane Perlez reported that American
        officials had blocked a proposed purchase of a controlling stake in a
        unit of the Dutch electronics company Philips by Chinese investors
        because the United States was fearful the deal would be used to
        further China’s push into microchips.

        At the center of the concerns was a material called gallium nitride,
        which was being used by the Philips unit in light-emitting diodes, but
        which has applications for military and space and can be helpful in
        semiconductors. The report illustrated how American officials have
        come to view China’s large and growing tech industry with misgivings.

        At the same time, Jonathan Soble and Paul Mozur reported that Sharp,
        one of Japan’s large consumer electronics companies and the biggest
        LCD producer, was leaning toward a takeover offer from the Taiwanese
        contract manufacturer Foxconn. The news underlined the decline of
        Japan’s once-famed consumer electronics companies, which have been
        undercut in recent years by lower-cost competition from China and
        South Korea."""

        self.PARSER = English(serializer=False, matcher=False)

    def test_instanstiated_object_of_correct_type(self):
        gfg = GapFillGenerator(self.PARSER, self.SOURCE_TEXT,
                               [GapFillBlankType.named_entities])
        self.assertIsInstance(gfg, GapFillGenerator)

if __name__ == '__main__':
    unittest.main()
