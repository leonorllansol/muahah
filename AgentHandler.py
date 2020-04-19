import conversation
import configsparser
from dialog.SimpleQA import SimpleQA
from texttools.normalizers import normalizerFactory
from texttools.normalizers.normalizer import Normalizer
import AgentFactory
from xml.dom import minidom
import subprocess
import operator
import time
import DocumentManager
import agents

from os import path
import multiprocessing
from multiprocessing import Process



"""
The AgentManager class is responsible for instantiating all of the available external agents and gathering each of their responses when faced with a user query.

It communicates directly with the SaySomethingSmart module: a single object of AgentManager is instantiated from the side of SaySomethingSmart.py, and SaySomethingSmart is the module that calls the AgentManager.generateExternalAgentsAnswers() function.

The AgentManager also uses the AgentFactory library (located in /resources/externalAgents/), which has the main role of gathering all the files related to the available external agents and instantiating each one.

Finally, this module interacts with the LuceneWrapper java class for the purpose of executing searches in the corpus in order to gather the possible answer candidates for each agent.
"""


class AgentHandler:

    """
    __init__: Initialize the AgentManager object

    - New Conversation object
    - Retrieve ExternalAgentsPath from config.xml through configsparser
    - Initialize the avaiable external agents
    - Check the normalizers to use
    """
    def __init__(self, AMA_labels, covid_labels):
        self.AMA_labels = AMA_labels
        self.covid_labels = covid_labels
        self.conversation = conversation.Conversation()
        self.externalAgentsPath = configsparser.getExternalAgentsPath()
        self.externalAgents = self.initializeAgents()
        self.normalizers = normalizerFactory.createNormalizers(configsparser.getNormalizers())
        self.externalAgentsNames = list(map(lambda x: x.agentName if not x.agentName[-1] in ['1','2','3'] else x.agentName[:-1], self.externalAgents))


    """
    initializeAgents(self): Call AgentFactory lib in order to generate all available external agents
    Return array of externalAgents (ex: [<FaqsAgent Object>, <MixAgent Object>])
    """
    def initializeAgents(self):
        return AgentFactory.createExternalAgents(self.externalAgentsPath)

    """
        João's agents
    This function generates the answers for each external agent and returns them in the form of a dictionary

    :param query: The query introduced by the user.
    :return: A dictionary containing all of the answers given to the query by the external agents. {'agent':'answer'}
    """
    def generateExternalAgentsAnswers(self, query, query_labels):
        agentAnswers = {}

        t = time.time()

        candidates = DocumentManager.generateCandidates(query)

        # for i,c in enumerate(candidates):
        #     print(i,c.getQuestion())
        #     print(i,c.getAnswer())
        # print()

        print(self.__class__.__name__ + " Candidate generation time: " + str(time.time() - t))

        source = ""
        # {'agent': query}
        candidateQueryDict = {}
        for agent in self.externalAgents:
            # flag = False
            # for elem in configsparser.getActiveAgents():
            #     if agent.agentName.startswith(elem):
            #         flag = True
            #         break
            # if not flag:
            #     continue


            agentTime = time.time()

            try:
                if(agent.normalizeUserInput):
                    query = Normalizer().applyNormalizations(query, self.normalizers)
            except AttributeError:
                pass

            try:
                if agent.corpusPath:


                    if agent.__class__.__name__ == "GeneralAgent":
                        synonymsPath = "agents/externalAgents/GeneralAgent/" + agent.agentName + "/sinonimos.txt"
                        if not path.exists(synonymsPath):
                            synonymsPath = ""
                        acronymsPath = "agents/externalAgents/GeneralAgent/" + agent.agentName + "/acronimos.txt"
                        if not path.exists(acronymsPath):
                            acronymsPath = ""
                            
                        candidates = DocumentManager.generateCandidates(query,indexPath=agent.indexPath,corpusPath=agent.corpusPath, synonymsPath=synonymsPath, acronymsPath=acronymsPath)
                        answer, candidateQueryDict[agent.agentName] = agent.requestAnswer(query,candidates, query_labels)
                    else:
                        candidates = DocumentManager.generateCandidates(query,indexPath=agent.indexPath,corpusPath=agent.corpusPath)
                        answer = agent.requestAnswer(query,candidates)

                    #candidates = DocumentManager.generateCandidates(query)

            except AttributeError:
                if(len(candidates) > 0):
                    if agent.__class__.__name__ == "GeneralAgent":
                        answer, candidateQueryDict[agent.agentName] = agent.requestAnswer(query,candidates, query_labels)
                    else:
                        answer = agent.requestAnswer(query,candidates)
                else:
                    answer = configsparser.getNoAnswerMessage()




            try:
                if(answer == [] or answer == ""):
                    agentAnswers[agent.agentName] = configsparser.getNoAnswerMessage()
                else:
                    agentAnswers[agent.agentName] = answer
            except IndexError:
                agentAnswers[agent.agentName] = configsparser.getNoAnswerMessage()

            #print(agent.agentName + " execution time: " + str(time.time() - agentTime))

        for agent, answer in agentAnswers.items():
            if type(answer) is list:
                if not (type(answer[0]) is str):
                    agentAnswers[agent] = answer[0].getAnswer()
                else:
                    agentAnswers[agent] = answer[0]
            else:
                agentAnswers[agent] = answer

        return agentAnswers, candidateQueryDict

    def generateInternalAgentsAnswers(self, function, agents_dict: dict, query: str) -> dict:

        """
        Mariana's agents
        This function executes the agent's processes in parallel to optimize the time it takes to obtain all the answers from all the internal agents.

        :param function: The function to obtain the agent's answers.
        :param agents_dict: A dictionary containing all of the internal agents' informations contained in the agents config xml file
        :param query: The query introduced by the user.
        :return: A dictionary containing all of the answers given to the query by the agents.
        """

        pros = []
        manager = multiprocessing.Manager()
        answers = manager.dict()
        for agent in agents_dict:
            if not agent in self.externalAgentsNames:
                flag = False
                for elem in configsparser.getActiveAgents():
                    if agent == elem:
                        flag = True
                        break
                if not flag:
                    continue
                #if agents_dict[agent]['importPath'] not in agents.all_modules:
                    #raise Exception('\n\n!!!ERROR!!!\nConfigurations wrong in agents config file. '
                                    #'Check if the names are all correct and the folders are in the correct place. '
                                    #'Also check if you have an __init__.py file in your agents directory and if it '
                                    #'contains all the specified values.')
                method = agents_dict[agent]['methodName']
                path = agents_dict[agent]['path']
                import_path = agents_dict[agent]['importPath']
                labels = agents_dict[agent]['labels']
                p = Process(target=function, args=(agent, method, path, import_path, query, labels, answers))
                pros.append(p)
                p.start()
        for t in pros:
            t.join()
        return answers



    """
    generateExternalAgentsAnswersFixedCandidates(self, query, candidates): generates the answers for each agent and returns them in the form of a dictionary

    This function is similar to generateExternalAgentsAnswers(), with the difference that it takes the lucene candidates as a parameter instead of generating them in the function, which allows for the scores given to each candidate by all of the agents to be taken into consideration for other tasks

    query: String containing the user's input
    candidates: Array composed by the SimpleQA pairs generated by Lucene
    - Send the query and the candidates to each available external agent
    - Gather the answers of each agent and store them in the agentAnswers dictionary

    Return dictionary containing the answers of each agent
    Key (String): Name of the agent
    Value (String): Answer of the agent

    """

    def generateAgentsAnswersFixedCandidates(self, query, candidates):

        #print('++++++++++++++++++')
        #for c in candidates:
        #    print(c.getAnswer())
        #print('++++++++++++++++++')


        agentAnswers = {}
        additionalAnswers = []

        t = time.time()
        for agent in self.externalAgents:

            agentTime = time.time()

            try:
                if(agent.normalizeUserInput):
                    query = Normalizer().applyNormalizations(query, self.normalizers)
            except AttributeError:
                pass

            answer = agent.requestAnswer(query,candidates)
            #print(answer)
            #print(agent.agentName)
            #for a in answer:
            #    print(a.getAnswer())
            #print('--------------------*')

            try:
                if(type(answer) == str):
                    answer = [SimpleQA("","","",answer,answer,0)]
                    for a in self.externalAgents:
                        answer[0].scores[a.agentName] = 0
                    answer[0].scores[agent.agentName] = 1
                    additionalAnswers.append(answer[0])

                if(answer == [] or answer == ""):
                    agentAnswers[agent.agentName] = configsparser.getNoAnswerMessage()
                else:
                    agentAnswers[agent.agentName] = answer
            except IndexError:
                agentAnswers[agent.agentName] = configsparser.getNoAnswerMessage()

        for ad in additionalAnswers:
            candidates.append(ad)

            #print(agent.agentName + " execution time: " + str(time.time() - agentTime))
        return agentAnswers
