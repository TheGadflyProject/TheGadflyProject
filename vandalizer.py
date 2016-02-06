# !/usr/bin/python3

# Imports
#import nltk
import glob
import os
from Gadfly import SourceText
from GapFillGenerator import GapFillGenerator

# GLOBAL VARIABLES
# should probably refactor at some point
PROJECT_DIR = os.path.dirname(__file__)
NEWS_ARTICLES_DIR = os.path.join(PROJECT_DIR, "NewsArticles")

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
