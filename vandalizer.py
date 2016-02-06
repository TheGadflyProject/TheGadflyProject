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
        print("Reading file "+self.file)
        self.raw_text = self.load_text()
        print("Initializing: Text loaded.")
        self.pos_tagged_sents = self.store_pos()
        print("Initializing: POS Tagging complete.")
        #This is currently not being used anywhere
        # self._source_obj.derived_sents = self.pos_tagged_sents
        # # This is using the terminology from Heilman and Smith (2010)
        # # For now this does nothing special. Should later simplify sentences
        # # in various ways. Likely more derived sentences than in source text
        # print("Initializing: Deriving Sentences complete...")

    def load_text(self):
        f = open(self.file, encoding='utf-8')
        return f.readlines()

    def store_pos(self):
        pos_lst = []
        for line in self.raw_text:
            line = line.strip()
            if len(line) == 1:
                continue  # b/c readlines has empty lines for now
            sents = nltk.sent_tokenize(line)
            for sent in sents:
                tokenized = nltk.word_tokenize(sent)
                pos_lst.append(nltk.pos_tag(tokenized))
        return pos_lst

    

class GapFillGenerator:

    def __init__(self, source_obj):
        self._source_obj = source_obj

    def question_generation(self,selected_sents):
        """ Remove blank and display question"""
        possible_questions = []
        for sent in selected_sents:
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
        

    def sentence_simplification(self):
        pass

    def sentence_selection(self):
        """ Later: Select by some notion of a good sentence.
        Soon: Select by not having annoying anaphora, etc.
        Now: Select by not having PRP or PRP$.
        """
        selected_sent_lst = []
        count_bad = 0
        for sent in self._source_obj.pos_tagged_sents:
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
        print("Good sentences = {}".format(len(self._source_obj.pos_tagged_sents)-count_bad))
        return selected_sent_lst

    def print_questions(self, outputFile):
        for n, (question, answer) in enumerate(self.questions):
            outputFile.write("\nQuestion #{}\n".format(n+1))
            outputFile.write(
                "Q: {}".format(question.encode('ascii', 'ignore'))
                )
            outputFile.write(
                "A: {}\n".format(answer.encode('ascii', 'ignore'))
                )
        outputFile.write("")

    def run(self):
        #This step of filtering can alternatively happen at the level of filterning questions
        self.selected_sents = self.sentence_selection()
        print("Initializing: Sentence Selection complete.")

        self.questions = self.question_generation(self.selected_sents)
        print("Initializing: Question generation complete.")

    def question_count(self):
        return len(self.questions)

##############################################################################

def main():
    #This needs to go into a setup file.
    #nltk.download(['punkt', 'averaged_perceptron_tagger'])
    news_articles = os.path.join(NEWS_ARTICLES_DIR, "*.txt")
    outputFile = open("output.txt","w")
    for file in glob.glob(news_articles):
        article = SourceText(file)
        generator = GapFillGenerator(article)
        generator.run()
        generator.print_questions(outputFile)
        print("This found {} questions from the text.".format(
            generator.question_count()))

##############################################################################


if __name__ == '__main__':
    main()
