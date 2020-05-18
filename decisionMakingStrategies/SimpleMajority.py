import operator
import os,sys,inspect

# to import file from main directory
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(current_dir)

from DecisionMethod import DecisionMethod
import configsparser, dialog


class SimpleMajority(DecisionMethod):
    # Given a set of answers, delivers the most frequent answer to the user

    def getAnswer(self, answers):
        answerFrequency = {}
        try:
            for agent in answers.keys():
                if(type(answers[agent]) is list):
                    answers[agent] = answers[agent][0]

                answer = answers[agent]

                if(type(answer) is dialog.SimpleQA.SimpleQA):
                    answer = answer.getAnswer()

                answerFrequency[answer] = answerFrequency.get(answer,0) + 1

            return max(answerFrequency.items(),key=operator.itemgetter(1))[0]

        except ValueError:
            return configsparser.getNoAnswerMessage()
