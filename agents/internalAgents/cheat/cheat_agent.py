import pickle, os, random, string, unicodedata
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
#nltk.download('punkt')
#nltk.download('stopwords')

curr_dir = os.path.dirname(os.path.abspath(__file__)) + '/'


def cheating_dialog(query: str) -> str:
    
    """
    This function receives a query and returns an answer to that query using some simple rules of just matching a
    specific query to a pre-made answer.

    :param query: A query introduced in the system by an user.
    :return: An answer to the introduced query.
    """

    yn_model = pickle.load(open(curr_dir + 'YN_model.sav', 'rb'))
    qnq_model = pickle.load(open(curr_dir + 'QNQ_model.sav', 'rb'))
    data = pd.DataFrame([[query]], columns=['query'])
    data = data['query']
    prediction_qnq = qnq_model.predict(data)[0]
    prediction_yn = ''

    stripped_query = ''.join((c for c in unicodedata.normalize('NFD', query) if unicodedata.category(c) != 'Mn')).lower().translate(str.maketrans('', '', string.punctuation))
    tokenized_query = word_tokenize(stripped_query.lower())

    so_file = open(curr_dir + 'SOCIAL.txt', 'r')
    so_list = [s.rstrip() for s in list(so_file)]
    so_query_list = [s.split('\t')[0] for s in so_list]
    so_answer_list = [s.split('\t')[1] for s in so_list]
    if prediction_qnq == 'QUESTION':
        prediction_yn = yn_model.predict(data)[0]

    matching = [s for s in so_query_list if stripped_query in s]
    if len(matching) >= 1:
        return so_answer_list[so_query_list.index(matching[0])]

    if 'ou' in tokenized_query:
        return stripped_query[stripped_query.index('ou') + 3].upper() + stripped_query[stripped_query.index('ou') + 4: ] + '.'

    if prediction_yn == 'YN_QUESTION':
        yn_answers_file = open(curr_dir + 'YN_ANSWERS.txt', 'r')
        yn_list = [s.rstrip() for s in list(yn_answers_file)]
        return random.choice(yn_list)

    return 'Essa não é a minha área de especialidade.'

