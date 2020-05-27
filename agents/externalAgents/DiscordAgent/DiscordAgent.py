import re
import json

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Agent import Agent

class DiscordAgent(Agent):
    def __init__(self,configs):
        super(DiscordAgent, self).__init__(configs)
        self.jsonPath = configs['jsonPath']
        self.internalData = json.load(open(self.jsonPath,'r+',encoding='utf8'))
        self.qaPairs = self.mapJsonData(self.internalData)



    def requestAnswer(self,userInput):

        if(userInput in self.qaPairs.keys()):
            return self.qaPairs[userInput]
        else:
            return []

        # ADD NORMALIZING, LOWERCASING AND SPECIFIC CASES


    def mapJsonData(self,jsonData):
        map = {}
        for sequence in jsonData['sequences']:
            for pair in sequence:
                if(pair['posReacts'] > pair['negReacts']):
                    map[pair['query']] = pair['answer']
        return map
