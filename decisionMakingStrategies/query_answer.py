import operator
import os,sys,inspect

# to import file from main directory
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(current_dir)

from DecisionMethod import DecisionMethod
import classificationAndMatching.query_answer_label_match as query_answer_label_match

class query_answer(DecisionMethod):
    # The labels of the agent's answer are compared with the labels of the query, obtained from a machine learning module.
    def getAnswer(self, answers, query_labels, corpora_dict, answer_label_dict):
        list_of_answers = [a[0] for a in answers.values()]
        temp_dict = query_answer_label_match.answer_classification(corpora_dict['answer'], list_of_answers,
                                                                    query_labels)[0]
        temp_score_dict = {answer: 0.0 for answer in list_of_answers}
        temp_score_dict = {answer: temp_dict[answer] + temp_score_dict[answer] for answer in temp_dict}
        for answer in list_of_answers:
            if answer not in temp_score_dict:
                temp_score_dict[answer] = 0.0
        answer_label_dict_aux = query_answer_label_match.answer_classification(corpora_dict['answer'], list_of_answers,
                                                                            query_labels)[1]

        # answer_label_dict = {answer: list(set(answer_label_dict[answer] + answer_label_dict_aux[answer]))
        #                     for answer in answer_label_dict_aux if answer_label_dict_aux[answer]}
        answer_label_dict = {answer: answer_label_dict[answer] + answer_label_dict_aux[answer]
                            for answer in answer_label_dict_aux if answer_label_dict_aux[answer]}


        return max(temp_score_dict.items(), key=operator.itemgetter(1))[0], answer_label_dict
