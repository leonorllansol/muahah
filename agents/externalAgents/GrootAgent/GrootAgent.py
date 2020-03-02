class GrootAgent:
    def __init__(self,configs):
        self.agentName = self.__class__.__name__

    def requestAnswer(self,userInput,candidates):

        for c in candidates:
            
            questionWords = self.getWordSet(c.getNormalizedQuestion())
            answerWords = self.getWordSet(c.getNormalizedAnswer())

            if("groot" in questionWords or "groot" in answerWords):
                c.addScore(self.agentName, 1)
            else:
                c.addScore(self.agentName, 0)

        return "I am Groot!"
    

    def getWordSet(self,input):
        #tokenizedInput = re.sub(r'\W+',' ',input).lower()
        #wordSet = set(tokenizedInput.split())
        wordSet = set(input.split())
        return wordSet