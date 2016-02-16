from question import Question
import collections


class GapFillGenerator:

    GAP_FILL = "GAP_FILL"

    def __init__(self, source_text_obj):
        self._source_text_obj = source_text_obj

    def generate_questions(self, selected_sents):
        """ Remove blank and display question"""
        possible_questions = []
        for sent in selected_sents:
            last_n = -2  # random initialization?
            last_answer = ""
            last_temp_sent = ""
            for n, (token, pos) in enumerate(sent):
                if pos in ["NNP", "NNPS"]:
                    if n-1 == last_n:
                        # deals (poorly) with NNP/NNPS phrases
                        answer = last_answer + " " + token
                        last_temp_sent[n] = ""
                        temp_sent = last_temp_sent
                        # removes the previous entry which
                        # had only half the phrase
                        possible_questions.pop()
                    else:
                        answer = token
                        temp_sent_original = [token for token, pos in sent]
                        temp_sent = [token for token, pos in sent]
                        temp_sent[n] = "__________"
                    possible_questions.append(
                            Question(" ".join(temp_sent_original),
                                     " ".join(temp_sent),
                                     answer,
                                     self.GAP_FILL
                                     )
                            )
                    last_answer = answer
                    last_temp_sent = temp_sent
                    last_n = n
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
