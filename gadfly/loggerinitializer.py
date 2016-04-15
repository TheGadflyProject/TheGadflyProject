# !/usr/bin/python3
"""For reference see: https://aykutakin.wordpress.com/2013/08/06/
logging-to-console-and-file-in-python/"""

# Imports
import logging


def initialize_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler("logging_all.log", "w")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(name)s: %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
