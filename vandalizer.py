# !/usr/bin/python3

# Imports

from gadfly.mcq_generator import MCQGenerator
from gadfly.gap_fill_generator import GapFillGenerator
from gadfly.loggerinitializer import initialize_logger
import logging
import glob
import os
import re

initialize_logger()
logger = logging.getLogger("v")

# GLOBAL VARIABLES
# should probably refactor at some point
_PROJECT_DIR = os.path.dirname(__file__)
_NEWS_ARTICLES_DIR = os.path.join(_PROJECT_DIR, "news_articles")


def clean_text(article):
    article = (re.sub(("“"), '"', article))
    article = (re.sub(("”"), '"', article))
    article = (re.sub(("’"), "'", article))
    return (re.sub(("[\s*]"), " ", article))


def main():
    news_articles = os.path.join(_NEWS_ARTICLES_DIR, "*.txt")
    output_file = open("output.txt", "w")
    files = glob.glob(news_articles)
    logger.info("Processing {} file(s)".format(len(files)))
    for file_name in files:
        f = open(file_name, encoding='utf-8')
        article = clean_text(f.read())
        # generator = GapFillGenerator(article)
        generator = MCQGenerator(article)
        generator.output_questions(output_file=output_file)

if __name__ == '__main__':
    main()
