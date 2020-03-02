

def query_agent_label_match(query_labels: list, agents_dict: dict) -> dict:

    """
    This function receives the query's labels and the agent's labels and sees if the agent's label list contains any
    subset of the query's labels. If it does it receives the score provided in the agents config xml file by each label.
    The function returns a score dict with each agent's score upon performing a match between the agent and the query's
    labels.

    :param query_labels: A list containing the labels that the query was found to have by the classification module.
    :param agents_dict: A dictionary containing all of the agents' informations contained in the agents config xml file
    :return: A dictionary containing a score by agent according to how much labels each agent has with the query.
    """

    score_dict = {}
    for agent in agents_dict:
        labels = agents_dict[agent]['labels']
        for label in labels:
            if label in query_labels:
                if agent in score_dict:
                    score_dict[agent] += labels[label]
                else:
                    score_dict[agent] = labels[label]
        if not agent in score_dict:
            score_dict[agent] = 0.0

    return score_dict
