from AgentHandler import AgentHandler
import configsparser
from WM_BestCandidate import WM_BestCandidate
from WM_BestScoring import WM_BestScoring
import math
from texttools.normalizers import normalizerFactory
from texttools.normalizers.normalizer import Normalizer
from texttools.ReferenceCorpusParser import ReferenceCorpusParser
import operator
import DocumentManager

class WeightedMajority:

    def __init__(self):
        self.references = self.parseReferenceCorpus()
        self.agentManager = AgentHandler()
        self.agents = self.agentManager.externalAgents
        self.strategy = self.pickStrategy()
        self.normalizers = normalizerFactory.createNormalizers(configsparser.getNormalizers())
        self.inputSize = configsparser.getInputSize()
        print('Current strategy: ' + configsparser.getLearningStrategy())
        print('Current reward function basis: ' + type(self.strategy.similarityMeasure).__name__)
        print('Current decimal places (alpha): ' + str(configsparser.getDecimalPlaces()))
        print('Current eta factor (beta): ' + str(configsparser.getEtaFactor()))


    def learnWeights(self):

        weights = {}
        rewards = {}

        for agent in self.agents:
            weights[agent.agentName] = 1/len(self.agents)
            rewards[agent.agentName] = 0

        initialWeights = configsparser.getInitialWeights()
        
        if(initialWeights.keys() == weights.keys()):
            weights = initialWeights

        t = 1

        for ref in self.references:

            print("------------ ITERATION " + str(t) + " ------------")
            print("Reference Trigger: " + ref.trigger)
            print("Reference Answer: " + ref.answer)


            
            nquery = Normalizer().applyNormalizations(ref.trigger, self.normalizers)
            
            #Leonor - previously: self.DocumentManager.generateCandidates(nquery)
            candidates = DocumentManager.generateCandidates(nquery)
            
            if(len(candidates) == 0):
                continue

            answers = self.agentManager.generateAgentsAnswersFixedCandidates(nquery, candidates)

            votedAnswer = self.mostVotedSelection(weights, answers)
            print("Agents Answer: " + votedAnswer)

            totalWeight = 0

            for agent in self.agents:
                #print(agent.agentName)
                rewards[agent.agentName] += self.strategy.computeReward(candidates, ref.answer, agent.agentName)
                weights[agent.agentName] += self.strategy.updateWeight(rewards[agent.agentName])
                totalWeight += weights[agent.agentName]
                #print('+++++++')
                
            
            #distinct for loops because totalWeight is still being updated in the first loop
            for agent in self.agents:
                weights[agent.agentName] = (weights[agent.agentName] * 100) / totalWeight
            
            finalWeights = weights

            print(finalWeights)
            print()
            
            t += 1

            if(t > self.inputSize):
                break
   


    
    def mostVotedSelection(self, weights, answers):
        
        mostVoted = {}
        mostVoted[configsparser.getNoAnswerMessage()] = 0
        #print(answers)
        #we're assuming that all answers are represented by SimpleQA objects
        for agent in weights.keys():

            #must deal with the case that the agent doesn't have a set weight attribute, aka the default case: external structure being stored and passed?
            weightedVote = weights[agent]

            #assuming that the agentName attribute always exists for any agent

            bestCandidates = answers[agent]
            
            #print('-----------------')
            #print(agent)

            for bestCandidate in bestCandidates:

            #if(type(bestCandidate) is list):
            #    bestCandidate = bestCandidate[0]
                try:
                    bestAnswer = bestCandidate.getAnswer()
                    bestScore = bestCandidate.getScoreByEvaluator(agent)
                    if(bestAnswer in mostVoted.keys()):
                        mostVoted[bestAnswer] += weightedVote
                    else:
                        mostVoted[bestAnswer] = weightedVote
                except AttributeError:
                    mostVoted[configsparser.getNoAnswerMessage()] += 0.000000001   #low value; if no agents can answer the query, the no answer message will be the most voted
        
        
        #print(mostVoted)
        return max(mostVoted.items(), key=operator.itemgetter(1))[0]


    def pickStrategy(self):

        zeta = math.sqrt((configsparser.getEtaFactor() * math.log(len(self.agents))) / configsparser.getInputSize())
        decimalPlaces = configsparser.getDecimalPlaces()

        if(configsparser.getLearningStrategy() == "BestCandidate"):
            return WM_BestCandidate(decimalPlaces, zeta)

        elif(configsparser.getLearningStrategy() == "BestCandidate"):
            return WM_BestScoring(decimalPlaces, zeta)


    def parseReferenceCorpus(self):
        
        interactionsPath = configsparser.getInteractionsPath()
        linesPath = configsparser.getLinesPath()
        inputSize = configsparser.getInputSize()

        rcp = ReferenceCorpusParser(interactionsPath,linesPath,inputSize)

        return rcp.parse()


    def evaluation(self, agentWeights):
        accuracy = 0
        t = 1
        for ref in self.references:
            
            nquery = Normalizer().applyNormalizations(ref.trigger, self.normalizers)    
            candidates = DocumentManager.generateCandidates(nquery)
            
            if(len(candidates) == 0):
                continue

            answers = self.agentManager.generateAgentsAnswersFixedCandidates(nquery, candidates)
            votedAnswer = self.mostVotedSelection(agentWeights, answers)
            
            print('Reference: ' + ref.answer)
            print('Voted Answer: ' + votedAnswer)

            if(ref.answer.split() == votedAnswer.split()):
                accuracy += 1
                print('Accuracy: ' + str(accuracy))

            t += 1
            if(t > self.inputSize):
                break
        
        print('Accuracy before normalization: ' + str(accuracy))
        accuracy = (accuracy / self.inputSize) * 100

        print('Accuracy: ' + str(accuracy))
        
