import os, sys, inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
sys.path.append(current_dir)
import configsparser, WeightedMajority
from DecisionMethod import DecisionMethod

class WeightedVote(DecisionMethod):
    # Given a set of answers, chooses the one given by the agent with highest weight (from online learning)
    
    def getAnswer(self, answers):
        weights = configsparser.getWeightResults()
        wm = WeightedMajority.WeightedMajority()
        return wm.mostVotedSelection(weights, answers)
