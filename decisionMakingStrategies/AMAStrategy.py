import operator, string
import os,sys,inspect
from DecisionMethod import DecisionMethod

class AMAStrategy(DecisionMethod):
    # Given a set of answers, delivers one which contains "yes", "no" or "maybe"

    def getAnswer(self, answers):
        if "AMAAgent" in answers:
            return answers["AMAAgent"][0]
        else:
            return ""
