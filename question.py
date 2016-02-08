from enum import Enum

_QUESTION_TYPES = Enum('GapFill')


class Question:
    def __init__(self, question, answer):
        self._type = _QUESTION_TYPES.GapFill
        self.question = question
        self.answer = answer
