import operator, string
import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(current_dir)
from DecisionMethod import DecisionMethod

import configsparser, dialog


class AMAStrategy(DecisionMethod):
    # Given a set of answers, delivers one which contains "yes", "no" or "maybe"

    def getAnswer(self, answers):
        if "AMAAgent" in answers:
            return answers["AMAAgent"][0]
        else:
            return ""
