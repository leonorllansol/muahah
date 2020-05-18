import subprocess

class SimpleQA:
    def __init__(self, previousQA, question, normalizedQuestion, answer, normalizedAnswer, diff):
        self.previousQA = previousQA    #is a number
        self.question = question
        self.answer = answer
        self.normalizedAnswer = normalizedAnswer
        self.normalizedQuestion = normalizedQuestion
        self.diff = diff
        self.scores = {}

    def getDiff(self):
        return self.diff

    def getQuestion(self):
        return self.question

    def getAnswer(self):
        return self.answer

    def getNormalizedQuestion(self):
        return self.normalizedQuestion

    def getNormalizedAnswer(self):
        return self.normalizedAnswer

    def addScore(self, evaluator, score):
        self.scores[evaluator] = score

    def getScores(self):
        return self.scores

    def getScoreByEvaluator(self, evaluator):
        return self.scores[evaluator]

    def textual(self):
        return "previousQA: " + str(self.previousQA) + "; question: " + self.question +\
                "; answer: " + self.answer + "; normalizedAnswer: " + self.normalizedAnswer +\
                "; normalizedQuestion: " + self.normalizedQuestion + "; diff: " + str(self.diff)
