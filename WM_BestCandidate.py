from similarity.SimilarityMeasure import CosineSimilarity, Jaccard
import math

class WM_BestCandidate:

    def __init__(self, decimalPlaces, zeta):
        self.decimalPlaces = decimalPlaces
        self.zeta = zeta
        self.similarityMeasure = Jaccard(1)

        
    def computeReward(self, candidates, reference, agentName):
        newReward = 0.0

        if(len(candidates) == 0 or len(reference) == 0):
            return 0

        bestCandidateAnswer = candidates[0].getAnswer()
        bestScore = 0

        for c in candidates:
            candidateScore = c.getScoreByEvaluator(agentName)
            if(candidateScore > bestScore):
                bestScore = candidateScore
                bestCandidateAnswer = c.getAnswer()


        newReward = self.rewardFunction(reference, bestCandidateAnswer)

        return (round(newReward * (10 ** self.decimalPlaces) / (10 ** self.decimalPlaces)))
    

    def updateWeight(self, reward):
        return math.exp(self.zeta * reward)


    def rewardFunction(self, reference, bestCandidate):    
        #print(bestCandidate)    
        #measure is jaccard distance, best result is 0
        similarity = 1 - self.similarityMeasure.distance(bestCandidate, reference)
        reward = min(similarity + 0.001, 1)
        #print(reward)
        return reward

