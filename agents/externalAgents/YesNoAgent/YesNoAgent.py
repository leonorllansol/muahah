import time,sys, os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Agent import Agent

class YesNoAgent(Agent):
    def __init__(self,configs):
        super(YesNoAgent, self).__init__(configs)
        self.questionSimValue = float(configs['questionSimValue'])
        self.answerSimValue = float(configs['answerSimValue'])
        self.normalizeUserInput = True



    def requestAnswer(self,userInput):
        candidates = self.candidates
        possibleAnswers = ["Sim.", "Não.", "Talvez."]

        for c in candidates:
            c.addScore(self.agentName, 0)

        # TODO ter em conta o contexto
        # TODO ver se há respostas nos candidates que contenham Sim, Não, Talvez
        finalAnswer = random.choice(possibleAnswers)

        return finalAnswer


    def getFinalScore(self,questionScore,answerScore):
        return questionScore * self.questionSimValue + answerScore * self.answerSimValue
