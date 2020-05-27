import re
from texttools import stopwords

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Agent import Agent

class EdgarEngAgent(Agent):
    def __init__(self,configs):
        super(EdgarEngAgent, self).__init__(configs)
        self.corpusPath = configs['corpusPath']
        self.dbPath = configs['dbPath']
        self.indexPath = configs['indexPath']
        self.threshold = float(configs['threshold'])
        self.stopwordsPath = configs['stopwords']


    def requestAnswer(self,userInput):
        candidates = self.candidates
        
        userInputWords = self.getWordSet(userInput)
        userInputWords_WoStopwords = self.getStringListWithoutStopWords(userInputWords)

        if(len(candidates) > 0):
            bestPairs = [candidates[0]]

            for c in candidates:

                questionWords = self.getWordSet(c.getNormalizedQuestion())

                questionWords_WoStopwords = self.getStringListWithoutStopWords(questionWords)

                #score = len(userInputWords.intersection(questionWords)) / len(userInputWords.union(questionWords))
                score = len(userInputWords_WoStopwords.intersection(questionWords_WoStopwords)) / len(userInputWords_WoStopwords.union(questionWords_WoStopwords))
                c.addScore(self.agentName,score)
                #print(questionWords_WoStopwords, score)

                if(c.getScoreByEvaluator(self.agentName) > bestPairs[0].getScoreByEvaluator(self.agentName)):
                    bestPairs = [c]
                elif(c.getScoreByEvaluator(self.agentName) == bestPairs[0].getScoreByEvaluator(self.agentName)):
                    bestPairs.append(c)
        else:
            return ["I'm sorry, but I do not know how to answer that."]

        if(bestPairs[0].getScoreByEvaluator(self.agentName) > self.threshold):
            return bestPairs
        else:
            return ["I'm sorry, but I do not know how to answer that."]



    def getWordSet(self,input):
        tokenizedInput = re.sub(r'\W+',' ',input).lower()
        wordSet = set(tokenizedInput.split())
        #wordSet = set(input.split())
        return wordSet


    def getStringListWithoutStopWords(self,tokenizedQuestion):
        stopWords = self.getStopWords()
        stringList = []
        for word in tokenizedQuestion:
            if not word in stopWords:
                stringList.append(word)
        return set(stringList)

    def getStopWords(self):
        path = self.stopwordsPath
        f = open(path, 'r', encoding='latin-1')
        stopwords = []
        lines = f.readlines()[16:]
        for line in lines:
            stopwords.append(line.split()[0])
        return stopwords
