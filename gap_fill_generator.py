from question import Question
from grammar_utilities import Chunker
import collections


class GapFillGenerator:

    GAP_FILL = "GAP_FILL"

    def __init__(self, source_text_obj):
        self._source_text_obj = source_text_obj

    def chunk_sentence(self, sents, chunker):
        chunkedlist = []
        for sent in sents:
            chunks = chunker(sent)
            for chunk in chunks:
                if(type(chunk) == type(chunks)):
                    temp = ''
                    for leaf in chunk.leaves():
                        temp += leaf[0]+' '
                    chunkedlist.append(temp)
        return chunkedlist

    def generate_questions(self, selected_sents):
        """ Remove blank and display question"""
        chunker = Chunker()
        possible_questions = []
        for sent in selected_sents:
            chunks = self.chunk_sentence(
                [sent], chunker.proper_noun_phrase_chunker)
            if len(chunks) != 0:
                temp_sent = [token for token, pos in sent]
                for chunk in chunks:
                    temp_question = " ".join(temp_sent)
                    temp_question = temp_question.replace(chunk, "__________ ")
                    possible_questions.append(
                            Question(temp_question,
                                     chunk.strip(),
                                     self.GAP_FILL
                                     ))
        return possible_questions

    def select_sentences(self):
        """ Later: Select by some notion of a good sentence.
        Soon: Select by not having annoying anaphora, etc.
        Now: Select by not having PRP or PRP$.
        """
        selected_sent_lst = []
        count_bad = 0
        for sent in self._source_text_obj.pos_tagged_sents:
            flag = False
            for token, pos in sent:
                if pos in ["PRP", "PRP$"]:
                    count_bad += 1
                    flag = True
                    break
            if flag is False:
                selected_sent_lst.append(sent)
        # This is garbage metrics for now:
        print("Bad sentences = {}".format(count_bad))
        print("Good sentences = {}".format(
            len(self._source_text_obj.pos_tagged_sents)-count_bad)
            )
        return selected_sent_lst

    def output_questions_to_file(self, output_file):
        for n, q in enumerate(self.questions):
            output_file.write("\nQuestion #{}\n".format(n+1))
            output_file.write(
                "Q: {}".format(
                    q.question.encode('ascii', 'ignore')
                    )
                )
            output_file.write(
                "A: {}\n".format(
                    q.answer.encode('ascii', 'ignore')
                    )
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

    def run(self):
        # This step of filtering can alternatively happen
        # at the level of filterning questions
        self.selected_sents = self.select_sentences()
        print("Initializing: Sentence Selection complete.")

        self.questions = self.generate_questions(self.selected_sents)
        print("Initializing: Question generation complete.")

    def question_count(self):
        return len(self.questions)
