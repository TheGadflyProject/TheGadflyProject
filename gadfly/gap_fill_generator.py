from gadfly.question import Question
from gadfly.sentence_summarizer import FrequencySummarizer, TF_IDFSummarizer
import string
import re


class GapFillGenerator:
    GAP_FILL = "GAP_FILL"
    _GAP = "___________"
    _PUNCTUATION = list(string.punctuation)

    def __init__(self, parser, source_text):
        self._source_text = source_text
        self._parsed_text = parser(self._source_text)
        self._exclude_named_ent_types = ["DATE",
                                         "TIME",
                                         "PERCENT",
                                         "CARDINAL",
                                         "MONEY",
                                         "ORDINAL",
                                         "QUANTITY"]
        self.questions = self.generate_questions()

    def find_named_entities(self):
        entities = set()
        for ent in self._parsed_text.ents:
            if (ent.label_ != "" and
               ent.label_ not in self._exclude_named_ent_types):
                entities.add(ent.text_with_ws)
        return entities

    def summarize_sentences(self):
        option = 1
        if option == 0:
            selector = FrequencySummarizer()
            sents = []
            for span in self._parsed_text.sents:
                sent = [self._parsed_text[i] for i in range(span.start, span.end)]
                tokens = []
                for token in sent:
                    tokens.append(token.text)
                sents.append(tokens)        
        else: # I messed w/ the below to get access to the lemma in my summarizer - DSG
            selector = TF_IDFSummarizer()
            sents = []
            for span in self._parsed_text.sents:
                sents.append([self._parsed_text[i] for i in range(span.start, span.end)])
        sentences = selector.summarize(sents, round(len(sents)*.2))
        # print("There are {} sentences sent *TO* TF_IDFSummarizer.".format(len(sents)))
        # print("There are {} sentences returned *FROM* TF_IDFSummarizer.".format(len(sentences)))
        # for n, x in enumerate(sentences):
        #     print("This is sentence #{} of {}".format(n+1, len(sentences)))
        #     print(x)
        #     print()
        return sentences

    def generate_questions(self):
        """ Remove blank and display question"""
        question_set = set()
        entities = self.find_named_entities()
        most_important_sents = self.summarize_sentences()
        for sent in most_important_sents:
            for entity in entities:
                sent_ents = re.findall(entity, sent)
                if sent_ents:
                    for n in range(len(sent_ents)):
                        gap_fill_question = self._replaceNth(sent,
                                                             entity,
                                                             "_____",
                                                             n
                                                             )

                        question = Question(sent,
                                            gap_fill_question,
                                            entity,
                                            self.GAP_FILL,
                                            )
                        question_set.add(question)

            return question_set

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
