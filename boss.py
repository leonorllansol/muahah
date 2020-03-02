import operator, classification, plug_and_play, query_agent_label_match, query_answer_label_match
from agents import *
import multiprocessing
import numpy as np
import os
from multiprocessing import Process
import configsparser
from DefaultAnswers import HighestWeightedScoreSelection, MultipleAnswerSelection
import logging, sys, time
import subprocess
from Decisor import Decisor
from AgentHandler import AgentHandler
from WeightedMajority import WeightedMajority
import DocumentManager
import agents.internalAgents
import copy

curr_dir = os.path.dirname(os.path.abspath(__file__))


def dialogue(agents_dict, system_dict, corpora_dict):
    
    '''João'''
    defaultAgentsMode = configsparser.getDefaultAgentsMode()
    
    if(not configsparser.usePreviouslyCreatedIndex()):
        DocumentManager.createIndex(configsparser.getIndexPath(), configsparser.getCorpusPath()) 

    if(defaultAgentsMode == 'multi'):
        multiAgentAnswerMode(agents_dict, system_dict, corpora_dict)
    #elif(defaultAgentsMode == 'sequential'):
        #sequentialConversationMode()
    #elif(defaultAgentsMode == 'learning'):
        #learningMode()
    #elif(defaultAgentsMode == 'evaluation'):
        #evaluationMode()
    #else:
        #classicDialogueMode()

def multiAgentAnswerMode(agents_dict, system_dict, corpora_dict):
    """
    :param agents_dict: A dictionary containing all of the agents' informations contained in the agents config xml file
    :param system_dict: A dictionary containing all of the system information contained in the system config xml file
    :return: Not applicable.
    """
    agentManager = AgentHandler()
    decisionMethodsWeights = configsparser.getDecisionMethodsWeights()
    
    decisionMaker = Decisor(decisionMethodsWeights, system_dict, agents_dict, corpora_dict)
    

    while True:
        query = ""

        while (query == ""):
            query = input("Diga algo: \n")
            print()

        if query == "exit":
            break
        
        logging.basicConfig(filename='logs/log.txt', filemode='w', format='%(message)s', level=logging.INFO)

        # external agents (Joao)
        externalAgentsAnswers = agentManager.generateExternalAgentsAnswers(query)
     
        
        # Mariana's agents
        internalAgentsAnswers = agentManager.generateInternalAgentsAnswers(get_agent_answer, agents_dict, query)
        
        predictions_query = classification.predict(corpora_dict['query'], query, 'query')
        
        previousWeight = -1
        currStrategy = ""
        previousDict = copy.deepcopy(decisionMethodsWeights)
        # increase weights of decision making strategies according to query labels
        if "OR_QUESTION" in predictions_query:
            if decisionMethodsWeights["OrStrategy"] > 0:
                previousWeight = decisionMethodsWeights["OrStrategy"]
                decisionMethodsWeights["OrStrategy"] += 60
                currStrategy = "OrStrategy"
        elif "YN_QUESTION" in predictions_query:
            if decisionMethodsWeights["YesNoStrategy"] > 0:
                previousWeight = decisionMethodsWeights["YesNoStrategy"]
                decisionMethodsWeights["YesNoStrategy"] += 60
                currStrategy = "YesNoStrategy"
        
        # update weights of other strategies so that sum of dictionary is still 100
        if previousWeight != -1:
            # assuming that all weights sum to 100
            remainingWeights = 100 - decisionMethodsWeights[currStrategy]
            for strategy, w in decisionMethodsWeights.items():
                if strategy != currStrategy:
                    decisionMethodsWeights[strategy] /= (100 - previousWeight) / remainingWeights
        #print(decisionMethodsWeights)
        
        for agent,answer in internalAgentsAnswers.items():
            if isinstance(internalAgentsAnswers[agent], list) or len(internalAgentsAnswers[agent]) == 0:
                # delete empty answers
                del internalAgentsAnswers[agent]
            
        answer_by_strategy, answer_tags = decisionMaker.bestAnswerByStrategy(query, internalAgentsAnswers, externalAgentsAnswers, predictions_query)
        
        # score per answer based on config weights per strategy {'answer':weight}
        score_per_answer = {}
        for strategy in answer_by_strategy:
            if answer_by_strategy[strategy] != '':
                if answer_by_strategy[strategy] == configsparser.getNoAnswerMessage():
                    continue
                if answer_by_strategy[strategy] in score_per_answer:
                    score_per_answer[answer_by_strategy[strategy]] += decisionMethodsWeights[strategy]
                else:
                    score_per_answer[answer_by_strategy[strategy]] = decisionMethodsWeights[strategy]
        
        #print(score_per_answer)
        answer_max_weight = max(score_per_answer.items(), key=operator.itemgetter(1))[0]
        
        logging.info("Query: " + query)
        logging.info("Answer: " + answer_max_weight)


        print()
        print("Questão: ", query)
        print("Resposta: ", answer_max_weight)
        print()

        # repôr pesos
        decisionMethodsWeights = copy.deepcopy(previousDict)


def get_agent_answer(agent: str, method: str, path: str, import_path: str, query: str, labels: list, answer_list: dict)\
        -> dict:

    """
    This function receives an agent and all its information and instantiates the agent. Upon instantiating the agent, it
    calls its dialog method with the user's query and obtains an answer. In the end it returns the updated answer_list
    dictionary which now contains the new agent's answer.

    :param agent: Name of the agent of which we wish to obtain an answer from.
    :param method: Name of the method of the agent that returns the answer to a query.
    :param path: Path of the agent.
    :param import_path: Import path of the agent (path in the format of python import).
    :param query: Query that the user introduced.
    :param labels: Labels on which the agent is an expert on.
    :param answer_list: Dictionary to which we will add the new agent's answer.
    :return: The updated answer_list dictionary with the new agent's answer
    """

    # As each agent might use code that is in other folder within its directory, we must change the current working
    # directory to the agent's directory.

    os.chdir(path)

    # Create an instance of the agent with its import path, that should be "agents.agentfoldername.agentpythonfilename"
    #print("Import path")
    #print(import_path)
    module = eval(import_path)

    # Create through reflection the method that we will call to get the agent's answers

    method_to_call = getattr(module, method)
    answer = method_to_call(query)

    if len(answer) > 0 and answer[-1] == '\n':
        answer = answer[:-2]

    answer_list[agent] = answer

    return answer_list


if __name__ == "__main__":
    '''Mariana'''
    agents_dicti = configsparser.getAgentsProperties(curr_dir + '/config/agents_config.xml')
    corpora_dicti = configsparser.getCorporaProperties(curr_dir + '/config/corpora_config.xml')
    system_dicti = configsparser.getSystemProperties(curr_dir + '/config/config.xml')

    classification.train(corpora_dicti, 'query')
    classification.train(corpora_dicti, 'answer')
    
    dialogue(agents_dicti, system_dicti, corpora_dicti)
