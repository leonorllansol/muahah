import sys

class DecisionMethod:
    # abstract class, superclass of all decision methods
    def getAnswer(self, a):
        pass
    def getAnswer(self, a, b):
        pass
    def getAnswer(self, a, b, c):
        pass
    def getAnswer(self, a, b, c, d):
        pass
    
    def getPriority(self, agent, priorityDoc):
        if(agent in priorityDoc.keys()):
            return priorityDoc[agent]
        else:
            return sys.maxsize
    
