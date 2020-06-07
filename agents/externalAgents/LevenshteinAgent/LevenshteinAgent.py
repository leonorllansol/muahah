import time
import editdistance

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Agent import Agent


class LevenshteinAgent(Agent):
    def __init__(self,configs):
        super(LevenshteinAgent, self).__init__(configs)
        self.questionSimValue = float(configs['questionSimValue'])
        self.answerSimValue = float(configs['answerSimValue'])
        self.normalizeUserInput = False



    def requestAnswer(self,userInput):
        candidates = self.candidates
        t = time.time()

        userInputLower = userInput.lower()
        bestPairs = [candidates[0]]

        editDistanceTotalTime = 0

        for c in candidates:
            questionLower = c.getQuestion().lower()
            answerLower = c.getAnswer().lower()

            questionScore = editdistance.eval(userInputLower,questionLower)
            answerScore = editdistance.eval(userInputLower,answerLower)


            finalScore = self.getFinalScore(questionScore,answerScore)
            c.addScore(self.agentName,1/finalScore)

            try:
                if(c.getAnswer()[len(c.getAnswer())-1] != '?' and c != bestPairs[0]):
                    bestPairs.append(c)
            except IndexError:
                pass
        bestPairs.sort(key=lambda x: x.getScoreByEvaluator(self.agentName), reverse=True)
        return bestPairs[:self.answerAmount]


    def getFinalScore(self,questionScore,answerScore):
        return questionScore * self.questionSimValue + answerScore * self.answerSimValue

def getNormalizedError(sentence1, sentence2, score):
    minimum = abs(len(sentence1) - len(sentence2))
    maximum = max(len(sentence1), len(sentence2))
    print("minimum:", minimum)
    print("maximum:", maximum)
    normalized = (score - minimum) / (maximum - minimum)
    return normalized
