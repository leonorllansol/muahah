import re


class FaqsAgent:
    def __init__(self,configs):
        self.agentName = self.__class__.__name__
        self.normalizeUserInput = True
    

    def requestAnswer(self,userInput,candidates):
        
        userInputWords = self.getWordSet(userInput)
        bestPair = candidates[0]
        for c in candidates:
            questionWords = self.getWordSet(c.getNormalizedQuestion())
            score = len(userInputWords.intersection(questionWords)) / len(userInputWords.union(questionWords))
            c.addScore(self.agentName,score)

            if(c.getScoreByEvaluator(self.agentName) > bestPair.getScoreByEvaluator(self.agentName)):
                bestPair = c
        
        return bestPair.getAnswer()



    def getWordSet(self,input):
        #tokenizedInput = re.sub(r'\W+',' ',input).lower()
        #wordSet = set(tokenizedInput.split())
        wordSet = set(input.split())
        return wordSet


