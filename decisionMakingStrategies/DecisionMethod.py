import sys
from abc import ABC, abstractmethod

class DecisionMethod(ABC):
    # abstract class, superclass of all decision methods
    @abstractmethod
    def getAnswer(self, a):
        pass

    def getPriority(self, agent, priorityDoc):
        if(agent in priorityDoc.keys()):
            return priorityDoc[agent]
        else:
            return sys.maxsize
