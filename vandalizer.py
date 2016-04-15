# !/usr/bin/python3

# Imports
from gadfly.q_generator_base import tfidf, GapFillBlankType
from gadfly.mcq_generator import MCQGenerator
from gadfly.gap_fill_generator import GapFillGenerator
import glob
import os
import re


# common into third class later, tfidf and GAPFIllbalskdnfliasdf

# GLOBAL VARIABLES
# should probably refactor at some point
_PROJECT_DIR = os.path.dirname(__file__)
_NEWS_ARTICLES_DIR = os.path.join(_PROJECT_DIR, "news_articles")


def clean_text(article):
    article = (re.sub(("“"), '"', article))
    article = (re.sub(("”"), '"', article))
    article = (re.sub(("’"), "'", article))
    return (re.sub(("[\n*]"), " ", article))


def main():
    news_articles = os.path.join(_NEWS_ARTICLES_DIR, "*.txt")
    output_file = open("output.txt", "w")
    files = glob.glob(news_articles)
    blank_types = [GapFillBlankType.named_entities]
    print("Processing {} file(s)".format(len(files)))
    for file_name in files:
        f = open(file_name, encoding='utf-8')
        article = clean_text(f.read())
        # generator = GapFillGenerator(article, gap_types=blank_types,
        #                              summarizer=tfidf)
        generator = MCQGenerator(article, gap_types=blank_types,
                                 summarizer=tfidf)
        generator.output_questions_to_file(output_file)

if __name__ == '__main__':
    main()
