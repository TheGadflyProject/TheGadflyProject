from enum import Enum

QuestionTypes = Enum('GapFill')


class Question:
    def __init__(self, question, answer):
        self._type = QuestionTypes.GapFill
        self.question = question
        self.answer = answer
