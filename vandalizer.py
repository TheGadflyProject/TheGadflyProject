# !/usr/bin/python3

# Imports
import nltk
import glob
import os
from gap_fill_generator import GapFillGenerator
from source_text import SourceText

# GLOBAL VARIABLES
# should probably refactor at some point
PROJECT_DIR = os.path.dirname(__file__)
NEWS_ARTICLES_DIR = os.path.join(PROJECT_DIR, "news_articles")

##############################################################################


def main():
    # This needs to go into a setup file.
    nltk.download(['punkt', 'averaged_perceptron_tagger'])
    news_articles = os.path.join(NEWS_ARTICLES_DIR, "*.txt")
    output_file = open("output.txt", "w")
    for file in glob.glob(news_articles):
        article = SourceText(file)
        generator = GapFillGenerator(article)
        generator.run()
        generator.output_questions_to_file(output_file)
        print("This found {} questions from the text.\n".format(
            generator.question_count()))

##############################################################################


if __name__ == '__main__':
    main()
