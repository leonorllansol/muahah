import operator, string
import os,sys,inspect

# to import file from main directory
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(current_dir)
# to import file from OrAgent directory
sys.path.append(parent_dir + "/agents/externalAgents/OrAgent/")
from DecisionMethod import DecisionMethod
import configsparser, dialog
import noun_chunks


class OrStrategy(DecisionMethod):
    # Given a set of answers, delivers one which contains "NP before or" or "NP after or"

    def getAnswer(self, answers, query):
        answerFrequency = {}
        np_before_or = ""
        np_after_or = ""
        try:
            if ("ou" in query.split()):
                np_before_or = noun_chunks.get_noun_phrase_before_or(query)
                if type(np_before_or) is list and len(np_before_or) > 0:
                    np_before_or = np_before_or[0]
                np_after_or = noun_chunks.get_noun_phrase_after_or(query)
                if type(np_after_or) is list and len(np_after_or) > 0:
                    np_after_or = np_after_or[0]
            else:
                raise ValueError

            for agent in answers.keys():
                if(type(answers[agent]) is list):
                    answers[agent] = answers[agent][0]

                answer = answers[agent]

                if(type(answer) is dialog.SimpleQA.SimpleQA):
                    answer = answer.getAnswer()

                # check if answer does not contain query to avoid choosing answer "consta que no results were found..."
                if not query.translate(str.maketrans('', '', string.punctuation)) in answer:
                    if np_before_or in answer.lower() or np_after_or in answer.lower():
                        answerFrequency[answer] = answerFrequency.get(answer,0) + 1

            # TODO escolher com base no contexto e não só frequência
            return max(answerFrequency.items(),key=operator.itemgetter(1))[0]

        except ValueError:
            return configsparser.getNoAnswerMessage()
