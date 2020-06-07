import time,os, sys, inspect
import spacy, random
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(current_dir)
import noun_chunks

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Agent import Agent

class OrAgent(Agent):
    def __init__(self,configs):
        super(OrAgent, self).__init__(configs)
        self.questionSimValue = float(configs['questionSimValue'])
        self.answerSimValue = float(configs['answerSimValue'])
        self.normalizeUserInput = True
        self.nlp = spacy.load("pt_core_news_sm")


    def requestAnswer(self,userInput):
        candidates = self.candidates
        for c in candidates:
            c.addScore(self.agentName, 0)
        if ("ou" in userInput.split()):
            np_before_or = noun_chunks.get_noun_phrase_before_or(userInput)
            np_after_or = noun_chunks.get_noun_phrase_after_or(userInput)

            if type(np_before_or) is list and len(np_before_or) > 0:
                np_before_or = np_before_or[0]
            if type(np_after_or) is list and len(np_after_or) > 0:
                    np_after_or = np_after_or[0]

            if np_before_or == '' and np_after_or == '':
                finalAnswer = ''
            elif np_before_or == '' and np_after_or != '':
                finalAnswer = np_after_or
            elif np_before_or != '' and np_after_or == '':
                finalAnswer = np_before_or
            else:
                nps = [np_before_or, np_after_or]
                # TODO ter em conta o contexto
                finalAnswer = random.choice(nps)
                print(finalAnswer)
            finalAnswer = finalAnswer.capitalize() + "."
        else:
            finalAnswer = ""

        return [finalAnswer]
