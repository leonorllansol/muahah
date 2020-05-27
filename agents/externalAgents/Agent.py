from abc import ABC, abstractmethod

class Agent(ABC):

    def __init__(self, configs):
        self.agentName = self.__class__.__name__
        super(Agent, self).__init__()
        
    def setCandidates(self, candidates):
        self.candidates = candidates

    @abstractmethod
    def requestAnswer(self, query):
        pass
