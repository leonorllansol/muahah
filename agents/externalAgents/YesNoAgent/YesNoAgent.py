import time,sys
import random

class YesNoAgent:
    def __init__(self,configs,indexval=''):
        self.agentName = self.__class__.__name__
        self.questionSimValue = float(configs['questionSimValue'])
        self.answerSimValue = float(configs['answerSimValue'])
        self.normalizeUserInput = True



    def requestAnswer(self,userInput,candidates):

        possibleAnswers = ["Sim.", "Não.", "Talvez."]
        
        for c in candidates:
            c.addScore(self.agentName, 0)
        
        # TODO ter em conta o contexto
        # TODO ver se há respostas nos candidates que contenham Sim, Não, Talvez 
        finalAnswer = random.choice(possibleAnswers)

        return finalAnswer


    def getFinalScore(self,questionScore,answerScore):
        return questionScore * self.questionSimValue + answerScore * self.answerSimValue
