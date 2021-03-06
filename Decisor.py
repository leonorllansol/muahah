import  operator
import configsparser
import sys, logging
import dialog
import importlib
# import personal_answers
import classificationAndMatching.classification as classification
import classificationAndMatching.query_agent_label_match as query_agent_label_match
import classificationAndMatching.query_answer_label_match as query_answer_label_match


"""
The Decisor class is responsible for deciding the best answer per strategy.

It receives the answers generated by the AgentHandler and DefaultAnswers modules, and returns a dictionary with the form {'strategy':'answer'}.

The current available decision making strategies are:
    SimpleMajority: Given a set of answers, delivers the most frequent answer to the user
    PrioritySystem: Given a set of answers, it returns the answer of the agent with higher priority, as defined in the config.xml
    AgentMultiAnswers: Same as SimpleMajority, but considering that an agent can return multiple answers
    PrioritySystemMultiAnswers: Same as PrioritySystem, but considering that an agent can return multiple answers
    PrioritySystemDevelopmentMulti: Similar to PrioritySystemMultiAnswers, but the user receives multiple possible answers to the sent query.
    WeightedVote: Given a set of answers, chooses the one given by the agent with highest weight (from online learning)
    query_agent: The labels of the agent's domain of expertise are compared with the labels of the query, obtained from a machine learning module.
    answer_personal: Given a set of answers, similarity measures are used to compare agents' answers to a corpus of answers. In this case, a query classified with label "PERSONAL" will be compared with a corpus of personal answers.
    answer_impersonal: Same as answer_personal, but a query classified with label "IMPERSONAL" will be compared with a corpus of impersonal answers.
    query_answer: The labels of the agent's answer are compared with the labels of the query, obtained from a machine learning module.

"""

class Decisor:

    # passing in constructor objects that don't change as the query changes
    def __init__(self, weights, system_dict, agents_dict, corpora_dict):
        self.decisionMethods = weights
        self.system_dict = system_dict
        self.agents_dict = agents_dict
        self.corpora_dict = corpora_dict

    """
    bestAnswerByStrategy(self, defaultAgentsAnswers, externalAgentsAnswers, query_labels): Upon receiving the answers from all available agents, decides the best answer to be delivered to the user

    :param defaultAgentsAnswers: Dictionary containing the answers of the default SSS agents in the format {'evaluator1': 'answer1', 'evaluator2': 'answer2'}
    :param externalAgentsAnswers: Dictionary containing the answers of all available external agents in the format {'agent1': 'answer1', 'agent2': 'answer2'}
    :param query_labels: list with the predicted labels for the query

    :return answer_by_strategy_dict: dictionary containing the answer chosen by each strategy
    :return answer_label_dict: dictionary containing the labels for each answer

    Sidenote: If none of the agents gave an answer, the default failure message is delivered (this message can be configured through the parameter <noAnswerFound> in the config.xml)
    """
    def bestAnswerByStrategy(self, query, defaultAgentsAnswers, externalAgentsAnswers, query_labels):

        # delete sentences like "Não sei responder a isso" when there are other answers
        def delete_escapings(agentAnswers):
            list_of_escapings = []
            # escape sentences João
            list_of_escapings.append(configsparser.getNoAnswerMessage())
            # escape sentences Mariana
            for agent in agentAnswers.keys():
                if agent in self.agents_dict and 'escapeSentences' in self.agents_dict[agent]:
                    for sentence in self.agents_dict[agent]['escapeSentences']:
                        list_of_escapings.append(sentence)

            # if all answers are escape sentences, I don't want to delete them
            flag = False
            for answerList in agentAnswers.values():
                for escaping in list_of_escapings:
                    try:
                        answerList.remove(escaping)
                    except ValueError:
                        pass

            return agentAnswers


        print("query labels::{}".format(query_labels))
        mergedAgentAnswers = {**defaultAgentsAnswers, **externalAgentsAnswers}

        answer_label_dict = {}
        for answerList in mergedAgentAnswers.values():
            for answer in answerList:
                answer_label_dict[answer] = []
        #answer_label_dict = {answer: [] for answer in mergedAgentAnswers.values()}

        answer_by_strategy_dict = {}

        for agent, answer in mergedAgentAnswers.items():
            print("Agente: ", agent, "; Resposta: \"", answer, "\"" )
        print()

        mergedAgentAnswers = delete_escapings(mergedAgentAnswers)


        # strategies that receive arguments other than the answers
        extra_args_by_strategy = { "query_agent": [query_labels, self.agents_dict],
                                "answer_impersonal": [query_labels, answer_label_dict],
                                "query_answer": [query_labels, self.corpora_dict, answer_label_dict],
                                "YesNoStrategy": [query], "OrStrategy": [query]}


        for strategyName, weight in self.decisionMethods.items():
            if strategyName == 'answer_impersonal' and not 'IMPERSONAL' in query_labels:
                continue
            # if strategyName == 'answer_personal' and not 'PERSONAL' in query_labels:
            #     continue
            mainClass = strategyName
            module = importlib.import_module('.' + mainClass,'decisionMakingStrategies')
            class_ = getattr(module,mainClass)

            answers = mergedAgentAnswers.copy()

            if self.decisionMethods[strategyName] > 0:

                s = class_(query) if strategyName == "answer_impersonal"  else class_()

                if strategyName in extra_args_by_strategy:

                    if answer_label_dict in extra_args_by_strategy[strategyName]:
                        answer_by_strategy_dict[strategyName], answer_label_dict = s.getAnswer(answers, *extra_args_by_strategy[strategyName])
                    else:
                        answer_by_strategy_dict[strategyName] = s.getAnswer(answers, *extra_args_by_strategy[strategyName])

                else:
                        answer_by_strategy_dict[strategyName] = s.getAnswer(answers)

                print("Usando o método " + strategyName + ", a resposta é \"" + answer_by_strategy_dict[strategyName] + "\".")


        return answer_by_strategy_dict, answer_label_dict
