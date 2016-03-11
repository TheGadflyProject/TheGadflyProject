# !/usr/bin/python3

# Imports
import glob
import os
from gadfly.gap_fill_generator import GapFillGenerator

# GLOBAL VARIABLES
# should probably refactor at some point
PROJECT_DIR = os.path.dirname(__file__)
NEWS_ARTICLES_DIR = os.path.join(PROJECT_DIR, "news_articles")


def main():
    news_articles = os.path.join(NEWS_ARTICLES_DIR, "Deal*.txt")
    output_file = open("output.txt", "w")
    files = glob.glob(news_articles)
    print("Processing {} file(s)".format(len(files)))
    for file_name in files:
        f = open(file_name, encoding='utf-8')
        article = f.read()
        generator = GapFillGenerator(article)
        # generator.output_questions_to_file(output_file)

if __name__ == '__main__':
    main()
