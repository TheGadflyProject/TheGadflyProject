from gadfly.question import Question
from spacy.en import English
import string
import re


class GapFillGenerator:
    GAP_FILL = "GAP_FILL"
    _GAP = "___________"
    _PUNCTUATION = list(string.punctuation)

    def __init__(self, source_text):
        self._source_text = source_text
        self._parser = English(serializer=False, matcher=False)
        self._parsed_text = self._parser(self._source_text, parse=False)
        self.questions = self.generate_questions()

    def find_named_entities(self):
        entities = set()
        for ent in self._parsed_text.ents:
            if (ent.label_ != "") and \
                (ent.label_ not in ["DATE", "TIME", "PERCENT", "CARDINAL"]):
                entities.add(ent.text_with_ws)
        return entities

    def generate_questions(self):
        """ Remove blank and display question"""
        question_set = set()
        entities = self.find_named_entities()
        for sent in self._parsed_text.sents:
            for entity in entities:
                sent_ents = re.findall(entity, sent.text)
                if sent_ents:
                    for n in range(len(sent_ents)):
                        gap_fill_question = self._replaceNth(sent.text,
                                                             entity,
                                                             self._GAP,
                                                             n
                                                             )
                        print(entity, ": ", gap_fill_question)
            #             question = Question(sent.text,
            #                                 gap_fill_question,
            #                                 entity,
            #                                 self.GAP_FILL,
            #                                 )
            #             question_set.add(question)
            # return question_set

    def _replaceNth(self, sent, old, new, n):
        """Replaces the old with new at the nth index in sent
        Cite:inspectorG4dget http://stackoverflow.com/a/27589436"""
        inds = [i for i in range(len(sent) - len(old)+1)
                if sent[i:i+len(old)] == old]
        if len(inds) < n:
            return  # or maybe raise an error
        # can't assign to string slices. So, let's listify
        sent_list = list(sent)
        # do n-1 because we start from the first occurrence of the string,
        # not the 0-th
        sent_list[inds[n-1]:inds[n-1]+len(old)] = new
        return ''.join(sent_list)

    def output_questions_to_file(self, output_file):
        for n, q in enumerate(self.questions):
            output_file.write("\nQuestion #{}\n".format(n+1))
            output_file.write(
                ", ".join(["Q: {}".format(q.question),
                "A: {}\n".format(q.answer)])
            )
        output_file.write("")
