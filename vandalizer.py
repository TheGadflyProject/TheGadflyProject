# !/usr/bin/python3

# Imports
import glob
import os
from gadfly.gap_fill_generator import GapFillGenerator, tfidf, frequency
from spacy.en import English

# GLOBAL VARIABLES
# should probably refactor at some point
_PROJECT_DIR = os.path.dirname(__file__)
_NEWS_ARTICLES_DIR = os.path.join(_PROJECT_DIR, "news_articles")
_PARSER = English(serializer=False, matcher=False)


def main():
    news_articles = os.path.join(_NEWS_ARTICLES_DIR, "*.txt")
    output_file = open("output.txt", "w")
    files = glob.glob(news_articles)
    print("Processing {} file(s)".format(len(files)))
    for file_name in files:
        f = open(file_name, encoding='utf-8')
        article = f.read()
        generator = GapFillGenerator(_PARSER, article, func=frequency)
        generator.output_questions_to_file(output_file)

if __name__ == '__main__':
    main()
