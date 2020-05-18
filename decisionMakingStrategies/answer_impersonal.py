import operator
import os,sys,inspect

from DecisionMethod import DecisionMethod
import impersonal_answers

class answer_impersonal(DecisionMethod):
    # Same as answer_personal, but a query classified with label "IMPERSONAL" will be compared with a corpus of impersonal answers.

    def __init__(self, query):
        self.query = query

    def getAnswer(self, answers, query_labels, answer_label_dict):
        list_of_answers = [a for a in answers.values()]
        temp_score_dict = {answer: 0.0 for answer in list_of_answers}
        li_roth = get_li_roth_labels(query_labels)

        temp_dict = {answer: impersonal_answers.answer_classification(self.query, li_roth[0], li_roth[1], answer)
                        for answer in list_of_answers}


        for answer, score in temp_dict.items():
            if temp_dict[answer][0]:
                answer_label_dict[answer] += temp_dict[answer][0]
                answer_label_dict[answer] = list(set(answer_label_dict[answer]))

        for answer, score in temp_dict.items():
            temp_score_dict[answer] += temp_dict[answer][1]

        return max(temp_score_dict.items(), key=operator.itemgetter(1))[0], answer_label_dict

def get_li_roth_labels (query_labels: list) -> list:

    """
    This function receives a list of labels and returns a list containing only the labels from the Li & Roth's taxonomy
    that are in the received list.

    :param query_labels: The labels that the query was found to have by the classification module.
    :return: A list containing the labels from the Li & Roth's taxonomy that are present in the list received as
    argument.
    """

    coarse_labels = ['ABBR', 'ENTY', 'DESC', 'HUM', 'NUM', 'LOC']
    fine_labels = ['code', 'count', 'date', 'dist', 'money', 'ord', 'period', 'perc', 'speed', 'temp',
                'volsize', 'weight', 'state', 'mount', 'country', 'city', 'gr', 'ind', 'title', 'desc', 'def',
                'manner', 'reason', 'animal', 'body', 'color', 'cremat', 'currency', 'dismed', 'dismed',
                'event', 'food', 'instru', 'lang', 'letter', 'plant', 'product', 'religion', 'sport',
                'substance', 'symbol', 'techmeth', 'termeq', 'veh', 'word', 'abb', 'exp', 'other']
    query_label_coarse = [label for label in query_labels if label in coarse_labels]
    query_label_fine = [label for label in query_labels if label in fine_labels]
    if not query_label_fine:
        query_label_fine = ['']
    if not query_label_coarse:
        query_label_coarse = ['']

    return query_label_coarse + query_label_fine
