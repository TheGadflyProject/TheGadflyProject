from enum import Enum
import nltk

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

QuestionTypes = Enum('QuestionTypes','GapFill WH')

class Question:
    def __init__(self):
        self._type = QuestionTypes.GapFill

    def setQuestion(text):
        self._question = text

    def setAnswer(text):
        self._answer = text

    def getQuestion():
        return self._question

    def getAnswer():
        return self._answer