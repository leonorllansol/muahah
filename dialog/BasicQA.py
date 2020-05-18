class BasicQA:
    def __init__(self, question, answer, normalizedQuestion, normalizedAnswer):
        self.question = question
        self.answer = answer
        self.normalizedAnswer = normalizedAnswer
        self.normalizedQuestion = normalizedQuestion

    def getQuestion(self):
        return self.question

    def getAnswer(self):
        return self.answer

    def getNormalizedQuestion(self):
        return self.normalizedQuestion

    def getNormalizedAnswer(self):
        return self.normalizedAnswer
