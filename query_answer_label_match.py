import classification


def answer_classification(corpora_dict: dict, answer_list: list, query_labels: list):

    """
    This function receives the query's labels and the answer's labels and sees if the answer's label list contains any
    subset of the query's labels. If it does it receives the 1 point per common label.
    The function returns a score dict with each answer's score upon performing a match between the answer and the query's
    labels.

    :param query_labels: A list containing the labels that the query was found to have by the classification module.
    :param answer_list: A list containing the all the answers to compare.
    :param corpora_dict:  a dictionary containing the information in the corpora config file.
    :return: A tuple containing: A dictionary containing a score by answer according to how much labels each agent
    has with the query; and a dictionary containing the labels found per answer.
    """

    score_dict = {answer: 0.0 for answer in answer_list}
    answers_labels_dict = {answer: [] for answer in answer_list}
    for answer in answer_list:
        answer_labels = classification.predict(corpora_dict, answer, 'answer')
        for label in answer_labels:
            if label in query_labels:
                score_dict[answer] += 1
            answers_labels_dict[answer].append(label)

    return score_dict, answers_labels_dict
