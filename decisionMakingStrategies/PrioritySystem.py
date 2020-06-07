import operator
import os,sys,inspect
# to import file from main directory
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(current_dir)
from DecisionMethod import DecisionMethod
import configsparser

class PrioritySystem(DecisionMethod):
    # Given a set of answers, it returns the answer of the agent with higher priority, as defined in the config.xml

    def getAnswer(self, answers):
        priorities = configsparser.getPriorities()
        finalAnswer = ""
        answerFrequency = {}

        for agent in answers.keys():
            if(type(answers[agent]) is list):
                answers[agent] = answers[agent][0]
                
            if(finalAnswer == ""):
                finalAnswer = (answers[agent],self.getPriority(agent,priorities))
                answerFrequency[answers[agent]] = answerFrequency.get(answers[agent],0) + 1
            else:
                if(self.getPriority(agent,priorities) < finalAnswer[1] and answers[agent] != configsparser.getNoAnswerMessage()):
                    finalAnswer = (answers[agent], self.getPriority(agent,priorities))
                else:
                    answerFrequency[answers[agent]] = answerFrequency.get(answers[agent],0) + 1

        if(finalAnswer[1] == sys.maxsize):
            return max(answerFrequency.items(),key=operator.itemgetter(1))[0]
        else:
            return finalAnswer[0]
