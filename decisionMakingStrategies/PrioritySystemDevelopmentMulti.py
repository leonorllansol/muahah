import operator
import os,sys,inspect

# to import file from main directory
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(current_dir)

from DecisionMethod import DecisionMethod
import configsparser, dialog


class PrioritySystemDevelopmentMulti(DecisionMethod):
    # Similar to PrioritySystemMultiAnswers, but the user receives multiple possible answers to the sent query.

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
                        finalAnswer = [(answer,self.getPriority(agent,priorities))]
                        answerFrequency[answer] = answerFrequency.get(answer,0) + 1
                    else:
                        break
                else:
                    if(self.getPriority(agent,priorities) < finalAnswer[0][1] and answer != configsparser.getNoAnswerMessage()):
                        finalAnswer = [(answer,self.getPriority(agent,priorities))]
                    elif(self.getPriority(agent,priorities) == finalAnswer[0][1] and answer != configsparser.getNoAnswerMessage() and (answer,self.getPriority(agent,priorities)) not in finalAnswer):
                        finalAnswer.append((answer,self.getPriority(agent,priorities)))
                    else:
                        answerFrequency[answer] = answerFrequency.get(answer,0) + 1

        if(finalAnswer == ""):
            return configsparser.getNoAnswerMessage()

        elif(finalAnswer[0][1] == sys.maxsize):
            if(configsparser.getAnswerAmount() > 1):
                compositeAnswer = ""
                answerItems = sorted(answerFrequency.items(),key=operator.itemgetter(1),reverse=True)
                i = 0
                while(i < len(answerItems) and i < configsparser.getAnswerAmount()):
                    compositeAnswer += str(i + 1) + ": " + answerItems[i][0] + "\n"
                    i += 1
                return compositeAnswer
            else:
                return max(answerFrequency.items(),key=operator.itemgetter(1))[0]
        else:
            if(configsparser.getAnswerAmount() > 1):
                compositeAnswer = ""
                answerItems = finalAnswer
                i = 0
                while(i < len(answerItems) and i < configsparser.getAnswerAmount()):
                    compositeAnswer += str(i + 1) + ": " + answerItems[i][0] + "\n"
                    i += 1
                return compositeAnswer
            else:
                return finalAnswer[0][0]
