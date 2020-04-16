import operator
import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(current_dir)
from DecisionMethod import DecisionMethod
import query_agent_label_match

class query_agent(DecisionMethod):
    # The labels of the agent's domain of expertise are compared with the labels of the query, obtained from a machine learning module.

    def getAnswer(self, query_labels, agents_dict, defaultAgentsAnswers):
         #for agent in mergedAgentAnswers.keys():
            #score_dict[agent] = 0.0
        score_dict = query_agent_label_match.query_agent_label_match(query_labels, agents_dict)
        to_delete = []
        for agent, score in score_dict.items():
            if not agent in defaultAgentsAnswers:
                to_delete.append(agent)
        for item in to_delete:
            del score_dict[item]

        agent_max_score = max(score_dict.items(), key=operator.itemgetter(1))[0]

        return defaultAgentsAnswers[agent_max_score]
