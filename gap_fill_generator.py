from question import Question
from grammar_utilities import Chunker
import collections
import string
from nltk.tree import Tree
import re

class GapFillGenerator:

    GAP_FILL = "GAP_FILL"
    GAP = "___________"

    def __init__(self, source_text_obj):
        self._source_text_obj = source_text_obj

        self.selected_sents = self.select_sentences()
        print("Initializing: Sentence Selection complete.")

        self.questions = self.generate_questions(self.selected_sents)
        print("Initializing: Question generation complete.")

    def select_sentences(self):
        """ Later: Select by some notion of a good sentence.
        Now: Select by all unless if having PRP/PRP$ not also having NNP/NNPS.
        """
        selected_sent_lst = []
        count_bad = 0
        for sent in self._source_text_obj.pos_tagged_sents:
            sent_pos = [pos for token, pos in sent]
            if "PRP" in sent_pos or "PRP$" in sent_pos:
                if "NNP" in sent_pos or "NNPS" in sent_pos:
                    selected_sent_lst.append(sent)
                else:
                    count_bad += 1
            else:
               selected_sent_lst.append(sent)
        # This is garbage metrics for now:
        print("Bad sentences = {}".format(count_bad))
        print("Good sentences = {}".format(
            len(self._source_text_obj.pos_tagged_sents)-count_bad)
            )
        return selected_sent_lst

    def generate_questions(self, selected_sents):
        """ Remove blank and display question"""
        question_set = set()
        chunker = Chunker()
        for sent in selected_sents:
            # The following is a hacky way to generate a sentence
            # TODO This should be improved, perhaps by passing the sentence from
            # SourceText
            source_sentence = " ".join([token for token, pos in sent])
            # remove space before punctuation
            source_sentence = \
                re.sub(r'\s([?.!,"](?:\s|$))', r'\1', source_sentence)

            chunk_tree = chunker.extended_proper_noun_phrase_chunker(sent)
            chunks = \
                [line.leaves() for line in chunk_tree if type(line) == Tree]
            for chunk in chunks:
                gap_phrase = [token for token, tag in chunk
                    if token not in list(string.punctuation)+['“']+['”']]
                if len(gap_phrase) > 0:
                    gap_phrase = " ".join(gap_phrase).strip()
                    for n in range(len(re.findall(gap_phrase, source_sentence))):
                        gap_fill_question = self._replaceNth(
                                                source_sentence,
                                                gap_phrase,
                                                self.GAP,
                                                n)
                        question = Question(
                            source_sentence,
                            gap_fill_question,
                            gap_phrase,
                            self.GAP_FILL,
                        )
                        question_set.add(question)
        return question_set

    def _replaceNth(self, sent, old, new, n):
        """Replaces the old with new at the nth index in sent
        Cite:inspectorG4dget http://stackoverflow.com/questions/27589325/how-to-find-and-replace-nth-occurence-of-word-in-a-sentence-using-python-regular
        """
        inds = [i for i in range(len(sent) - len(old)+1)
            if sent[i:i+len(old)]==old]
        if len(inds) < n:
            return  # or maybe raise an error
        sent_list = list(sent)  # can't assign to string slices. So, let's listify
        sent_list[inds[n-1]:inds[n-1]+len(old)] = new  # do n-1 because we start from the first occurrence of the string, not the 0-th
        return ''.join(sent_list)

    def output_questions_to_file(self, output_file):
        for n, q in enumerate(self.questions):
            output_file.write("\nQuestion #{}\n".format(n+1))
            output_file.write(
                "Q: {}".format(q.question)
                )
            output_file.write(
                "A: {}\n".format(q.answer)
                )
        output_file.write("")

    def _print_source_sentences(self):
        mapping = collections.defaultdict(list)
        for q in self.questions:
            mapping[q.source_sentence].append(q.question)
        for key, value in mapping.items():
            print(key, "\n")
            for val in value:
                print(val, "\n")
            print("_______________________________________________\n")
