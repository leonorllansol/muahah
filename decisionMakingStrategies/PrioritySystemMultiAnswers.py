import operator
import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
sys.path.append(current_dir)
from DecisionMethod import DecisionMethod
import configsparser, dialog


class PrioritySystemMultiAnswers(DecisionMethod):
    # Same as PrioritySystem, but considering that an agent can return multiple answers
    
    def getAnswer(self, answers):
        priorities = configsparser.getPriorities()
        finalAnswer = ""
        answerFrequency = {}

        for agent in answers.keys():
            
            if(type(answers[agent]) is str):
                answers[agent] = [answers[agent]]
            
            for answer in answers[agent]:
                if(type(answer) is dialog.SimpleQA.SimpleQA):
                    answer = answer.getAnswer()

                if(finalAnswer == ""):
                    if(answer != configsparser.getNoAnswerMessage()):
                        finalAnswer = (answer, self.getPriority(agent,priorities))
                        answerFrequency[answer] = answerFrequency.get(answer,0) + 1
                    else:
                        break
                else:
                    if(self.getPriority(agent,priorities) < finalAnswer[1] and answer != configsparser.getNoAnswerMessage()):
                        finalAnswer = (answer, self.getPriority(agent,priorities))
                    else:
                        answerFrequency[answer] = answerFrequency.get(answer,0) + 1


        if(finalAnswer == ""):
            return configsparser.getNoAnswerMessage()
        elif(finalAnswer[1] == sys.maxsize):
            return max(answerFrequency.items(),key=operator.itemgetter(1))[0]
        else:
            return finalAnswer[0]
