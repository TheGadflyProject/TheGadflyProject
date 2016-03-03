# !/usr/bin/python3

# Imports
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
    news_articles = os.path.join(NEWS_ARTICLES_DIR, "*.txt")
    sentence_file = open("sentence.txt", "w")
    question_file = open("question.txt", "w")
    for file in glob.glob(news_articles):
        article = SourceText(file)
        generator = GapFillGenerator(article)
        generator.run()
        generator.output_sentences_to_file(sentence_file)
        generator.output_questions_to_file(question_file)
        print("This found {} questions from the text.\n".format(
            generator.question_count()))
        generator._print_source_sentences()

##############################################################################


if __name__ == '__main__':
    main()
