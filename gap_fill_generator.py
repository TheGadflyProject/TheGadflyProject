from question import Question
from grammar_utilities import Chunker
import collections
import string
import csv

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

    def replaceNth(self, sent, old, new, n):
        """Replaces the old with new at the nth index in sent
        Cite:inspectorG4dget http://stackoverflow.com/questions/27589325/how-to-find-and-replace-nth-occurence-of-word-in-a-sentence-using-python-regular
        """
        inds = [i for i in range(len(sent) - len(old)+1) if sent[i:i+len(old)]==old]
        if len(inds) < n:
            return  # or maybe raise an error
        sent_list = list(sent)  # can't assign to string slices. So, let's listify
        sent_list[inds[n-1]:inds[n-1]+len(old)] = new  # do n-1 because we start from the first occurrence of the string, not the 0-th
        return ''.join(sent_list)

    def generate_questions(self, selected_sents):
        """ Remove blank and display question"""

        # fix leading space before punctuation  
        chunker = Chunker()
        possible_questions = []
        for sent in selected_sents:
            chunks = self.chunk_sentence(
                [sent], chunker.extended_proper_noun_phrase_chunker)
            chunks = [chunk.strip() for chunk in chunks]
            if len(chunks) != 0:
                temp_sent = [token for token, pos in sent]
                punctuation = list(string.punctuation)+['“']+['”']
                for chunk in chunks:
                    if chunk in punctuation: # solves punct as chunk problem. perhaps should move earlier?
                        continue
                    temp_question = " ".join(temp_sent)

                    # there HAS TO BE a better way than the below
                    temp_question = temp_question.replace(" .",".")
                    temp_question = temp_question.replace(" ,",",")
                    temp_question = temp_question.replace(" ?","?")
                    temp_question = temp_question.replace(" !","!")
                    
                    for n, each in enumerate(range(chunks.count(chunk))):
                        temp_question_with_blank = self.replaceNth(temp_question, chunk, "__________", n)
                        possible_questions.append((temp_question, # this process (list then object allows for set comparison)
                                     temp_question_with_blank,
                                     chunk, # I removed the .strip() b/c of line 45 b/c of the replaces in 55-58
                                     self.GAP_FILL)
                                     )

        return [Question(a,b,c,d) for a,b,c,d in set(possible_questions)]

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

    def output_questions_to_file(self, output_file):
        for q in self.questions:
            output_file.write("{}\n".format(q.question))
        output_file.write("")

    def output_sentences_to_file(self, output_file):
        for q in self.questions:
            output_file.write("{}\n".format(q.source_sentence))
        output_file.write("")

    def output_questions_to_csv(self, output_file):
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='|',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Sentence','Question'])
            for q in self.questions:
                writer.writerow([q.source_sentence, q.question])

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
