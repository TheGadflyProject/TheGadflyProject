# !/usr/bin/python3

# Imports
import nltk
import glob
import os


# GLOBAL VARIABLES
# should probably refactor at some point
PROJECT_DIR = os.path.dirname(__file__)
NEWS_ARTICLES_DIR = os.path.join(PROJECT_DIR, "NewsArticles")


class SourceText(object):
    """Understands source news text articles
    """
    def __init__(self, file):
        """This is initializing the class with a .txt file, running all
        transformations, selections, and question generation functions.
        """
        self.file = file
        self.raw = self.load_text()
        print("Initializing: Text loaded...")

        self.pos = self.store_pos()
        print("Initializing: POS complete...")

        self.derived_sents = self.pos
        # This is using the terminology from Heilman and Smith (2010)
        # For now this does nothing special. Should later simplify sentences
        # in various ways. Likely more derived sentences than in source text
        print("Initializing: Deriving Sentences complete...")

        self.selected_sents = self.select_sents()
        # ? - not sure if this should happen before or after above
        # likely depends on computational cost (?)
        print("Initializing: Selecting Sentences complete...")

        self.questions = self.create_questions()
        print("Initializing: Creating Questions complete...")

    def load_text(self):
        f = open(self.file, encoding='utf-8')
        return f.readlines()

    def store_pos(self):
        pos_lst = []
        for line in self.raw:
            line = line.strip()
            if len(line) == 1:
                continue  # b/c readlines has empty lines for now
            sents = nltk.sent_tokenize(line)
            for sent in sents:
                tokenized = nltk.word_tokenize(sent)
                pos_lst.append(nltk.pos_tag(tokenized))
        return pos_lst

    def select_sents(self):
        """ Later: Select by some notion of a good sentence.
        Soon: Select by not having annoying anaphora, etc.
        Now: Select by not having PRP or PRP$.
        """
        selected_sent_lst = []
        count_bad = 0
        for sent in self.pos:
            flag = False  # Sorry vijay
            for token, pos in sent:
                if pos in ["PRP", "PRP$"]:
                    count_bad += 1
                    flag = True
                    break
            if flag is False:
                selected_sent_lst.append(sent)
        # This is garbage metrics for now:
        print("Bad sentences = {}".format(count_bad))
        print("Good sentences = {}".format(len(self.pos)-count_bad))
        return selected_sent_lst

    def create_questions(self):
        """ Remove blank and display question"""
        possible_questions = []
        for sent in self.selected_sents:
            last_n = -2
            last_answer = ""
            last_temp_sent = ""
            for n, (token, pos) in enumerate(sent):
                if pos in ["NNP", "NNPS"]:

                    if n-1 == last_n:
                        # deals (poorly) with NNP/NNPS phrases
                        answer = last_answer + " " + token
                        last_temp_sent[n] = ""
                        temp_sent = last_temp_sent
                        possible_questions.pop()
                    else:
                        answer = token
                        temp_sent = [token for token, pos in sent]
                        temp_sent[n] = "__________"
                    possible_questions.append((" ".join(temp_sent), answer))
                    last_answer = answer
                    last_temp_sent = temp_sent
                    last_n = n
        return possible_questions

    def print_questions(self):
        for n, (question, answer) in enumerate(self.questions):
            print("\nQuestion #{}".format(n))
            print("Q: {}".format(question.encode('ascii', 'ignore')))
            print("A: {}".format(answer.encode('ascii', 'ignore')))

    def question_count(self):
        return len(self.questions)

##############################################################################


def main():
    nltk.download(['punkt', 'averaged_perceptron_tagger'])
    news_articles = os.path.join(NEWS_ARTICLES_DIR, "*.txt")
    for file in glob.glob(news_articles):
        article = SourceText(file)
        print("This found {} questions from the text.".format(
            article.question_count()))
        article.print_questions()

##############################################################################


if __name__ == '__main__':
    main()
