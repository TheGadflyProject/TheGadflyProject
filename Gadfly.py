from enum import Enum

QuestionTypes = Enum('GapFill')

class Question:
	def __init__(self):
		self._type = QuestionTypes.GapFill

	def setQuestion(text):
		self._question = text

	def setAnswer(text):
		self._answer = text

	def getQuestion():
		return self._question

	def getAnswer():
		return self._answer
	