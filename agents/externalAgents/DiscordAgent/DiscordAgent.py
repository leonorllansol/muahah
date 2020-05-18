import re
import json


class DiscordAgent:
    def __init__(self,configs):
        self.agentName = self.__class__.__name__
        self.jsonPath = configs['jsonPath']
        self.internalData = json.load(open(self.jsonPath,'r+',encoding='utf8'))
        self.qaPairs = self.mapJsonData(self.internalData)

    

    def requestAnswer(self,userInput,candidates):
        
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

