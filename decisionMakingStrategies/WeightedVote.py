import os, sys, inspect

# to import file from main directory
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(current_dir)

from DecisionMethod import DecisionMethod
import configsparser
from learning.WeightedMajority import WeightedMajority

class WeightedVote(DecisionMethod):
    # Given a set of answers, chooses the one given by the agent with highest weight (from online learning)

    def getAnswer(self, answers):
        weights = configsparser.getWeightResults()
        wm = WeightedMajority()
        return wm.mostVotedSelection(weights, answers)
