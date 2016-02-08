# ~/usr/bin/python3

import nltk

NLTK_PROJECT_MODULES = ["punkt", "averaged_perceptron_tagger"]


def main():
    print("Installing necessary NLTK Modules")
    nltk.download(NLTK_PROJECT_MODULES)


if __name__ == '__main__':
    main()
