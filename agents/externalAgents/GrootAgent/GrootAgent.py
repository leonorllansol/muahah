import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Agent import Agent

class GrootAgent(Agent):
    def __init__(self,configs):
        super(GrootAgent, self).__init__(configs)

    def requestAnswer(self,userInput):
        candidates = self.candidates
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
