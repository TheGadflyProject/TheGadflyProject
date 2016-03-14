import nltk


class SourceText(object):
    """Understands source news text articles
    """
    def __init__(self, raw_text):
        self.raw_text = raw_text
        print("Initializing: Text loaded.")
        self.pos_tagged_sents = self.pos_tag_sents()
        print("Initializing: POS Tagging complete.")

    def pos_tag_sents(self):
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
