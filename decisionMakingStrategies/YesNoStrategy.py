import operator, string
import os,sys,inspect

# to import file from main directory
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(current_dir)
from DecisionMethod import DecisionMethod
import configsparser, dialog


class YesNoStrategy(DecisionMethod):
    # Given a set of answers, delivers one which contains "yes", "no" or "maybe"

    def getAnswer(self, answers, query):
        answersWithYesNoFrequency = {}
        try:
            for agent in answers.keys():
                if(type(answers[agent]) is list):
                    answers[agent] = answers[agent][0]

                answer = answers[agent]

                if(type(answer) is dialog.SimpleQA.SimpleQA):
                    answer = answer.getAnswer()

                yesNoWords = ["sim", "não", "talvez"]

                for word in yesNoWords:
                    # check if answer does not contain query to avoid choosing answer "consta que no results were found..."
                    if not query.translate(str.maketrans('', '', string.punctuation)) in answer:
                        if word in answer.lower():
                            answersWithYesNoFrequency[answer] = answersWithYesNoFrequency.get(answer,0) + 1

            # TODO escolher com base no contexto e não só frequência
            return max(answersWithYesNoFrequency.items(),key=operator.itemgetter(1))[0]

        except ValueError:
            return configsparser.getNoAnswerMessage()
