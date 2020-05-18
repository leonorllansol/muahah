
class WM_BestScoring:

    def __init__(self, decimalPlaces, zeta):
        self.decimalPlaces = decimalPlaces
        self.zeta = zeta
        self.similarityMeasure = Jaccard(1)


    def computeReward(self, candidates, reference, agentName):

        newReward = 0

        for c in candidates:
            candidateScores = c.getScoreByEvaluator(agentName)
            newReward += self.rewardFunction(reference, c.getAnswer(), candidateScores)
        
        newReward = newReward / max(len(candidates), 1.0)
        
        return (round(newReward * (10 ** self.decimalPlaces)) / (10 ** self.decimalPlaces))
    
    
    def updateWeight(self, reward):
        return math.exp(self.zeta * reward)


    def rewardFunction(self, reference, candidate, score):
        tokenizedCandidate = candidate.split("\\s+")
        tokenizedReference = reference.split("\\s+")

        similarity = similarityMeasure.distance(tokenizedCandidate, tokenizedReference)

        reward = 1 - math.abs(similarity - score) + 0.001

        return reward