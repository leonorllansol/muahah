import pickle, os, re, copy, csv, treetaggerwrapper, nltk, random, spacy
import pandas as pd
from sklearn.pipeline import Pipeline
import numpy as np
from gensim.models import KeyedVectors
from nltk import TweetTokenizer
from sklearn.svm import LinearSVC, SVC, NuSVC
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier, RadiusNeighborsClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, BaggingClassifier, ExtraTreesClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.naive_bayes import GaussianNB, BernoulliNB, MultinomialNB, ComplementNB
from sklearn.model_selection import cross_val_score, cross_val_predict


curr_dir = os.path.dirname(os.path.abspath(__file__)) + '/'


def model_training(pandas_query, pandas_label, classifier, vectorizer, corpus_name: str, query_or_answer: str):

    """
    This function trains a given classifier with a given vectorizer with the provided queries and labels and creates
    a .sav file containing the model trained. This file is named corpus_name_model.sav under the folder models.

    :param pandas_query: A pandas dataframe column containing the queries that are to be used in the model training.
    :param pandas_label: A pandas dataframe column containing the labels that are to be used in the model training.
    :param classifier: The classifier (model) that is going to be trained.
    :param vectorizer: The vectorizer to be used in conjunction with the classifier.
    :param corpus_name: The name of the corpus that we are going to be using in the training of the model.
    :param query_or_answer: A string that indicates if the corpus is of answers or queries.
    :return: It does not return anything, however it creates a file .sav of the model.
    """

    pipe = Pipeline([('vectorizer', vectorizer), ('classifier', classifier)])
    pipe.fit(pandas_query, pandas_label)
    file_path = curr_dir + 'models/' + query_or_answer + '/' + corpus_name + "_model.sav"
    pickle.dump(pipe, open(file_path, 'wb'))


def model_loader(corpus_name: str, query_or_answer: str):

    """
    This function loads the model trained in the corpus named corpus_name that is within the file
    corpus_name_model.sav from the folder models and returns it to the user.

    :param corpus_name: The name of the corpus of witch we wish to retrieve the trained model.
    :param query_or_answer: A string that indicates if the corpus is of answers or queries.
    :return: The trained model on the corpus.
    """

    path = curr_dir + '/models/' + query_or_answer + '/' +  corpus_name + "_model.sav"
    return pickle.load(open(path, 'rb'))


def train(corpora_dict: dict, query_or_answer: str,
          generic_corpus_path='/corpora/query/Treino/questionNonQuestion.csv'):

    """
    This function trains the models mentioned in the corpora dictionary with the corpus in said dictionary and saves
    those models in the folder models. It takes into consideration the different kinds of specifities of the corpus
    such as their type of hierarchy and if they are specific or generic.

    :param corpora_dict: dictionary containing all the relevant information of the corpus to train models. This
    dictionary should have the same format as the one returned by the function corpora_xml_reader.
    :param query_or_answer: A string that indicates if the corpus is of answers or queries.
    :return: It does not return anything but it creates files with the trained models in the folder models.
    """

    def new_pandas_generator(query_column, label_column):
        new_pd = pd.DataFrame()
        new_pd[query_or_answer] = query_column
        new_pd['label'] = label_column
        return new_pd
    for corpus in corpora_dict[query_or_answer]:
        corpus_pandas = pd.read_csv(corpora_dict[query_or_answer][corpus]['path'], encoding='utf-8', sep='*')
        # Leonor - if + break
        if 'query' in corpus_pandas:
            model_training(corpus_pandas[query_or_answer], corpus_pandas[list(corpus_pandas)[0]], corpora_dict[query_or_answer][corpus]['classifier']
                        , corpora_dict[query_or_answer][corpus]['vectorizer'], corpus, query_or_answer)
        else:
            break;

        if 'subcorpus' in corpora_dict[query_or_answer][corpus]:
            # Recursively train subcorpus of the current corpus.
            train({query_or_answer: corpora_dict[query_or_answer][corpus]['subcorpus']}, query_or_answer)
        if 'sublabel' in corpora_dict[query_or_answer][corpus]:
            # Above this if, a model was already trained with the first label of a corpus with this kind of hierarchy
            # (the hierarchy sublabel). After this, for each label one level above in the hierarchy, a model is trained
            # containing the training for all the labels in the next level in the hierarchy.
            cross_scores = []
            #print(len(list(corpus_pandas['query'])))
            for i in range(eval(list(corpus_pandas)[0][-1]), eval(list(corpus_pandas)[-2][-1])):
                parent_label = 'label' + str(i)
                current_label = 'label' + str(i + 1)
                if current_label not in list(corpus_pandas):
                    break
                for c in list(corpus_pandas[parent_label].unique()):
                    # As the vectorizer and classifier is the same for all sublabels, but we only have one reference in
                    # memory in the corpora_dict, we perform a deep copy to generate more memory addresses with the same
                    # classifier and vectorizer.
                    vectorizer = copy.deepcopy(corpora_dict[query_or_answer][corpus]['sublabel'][0])
                    classifier = copy.deepcopy(corpora_dict[query_or_answer][corpus]['sublabel'][1])
                    sub_label_pandas = corpus_pandas[corpus_pandas[parent_label].str.match(c)][current_label]
                    sub_label_queries = corpus_pandas[corpus_pandas[parent_label].str.match(c)]['query']
                    model_training(sub_label_queries, sub_label_pandas, classifier, vectorizer, c, query_or_answer)
        if corpora_dict[query_or_answer][corpus]['corpusType'] == 'specific':
            # When a corpus is of type specific, a model is trained to identify if a query is generic or specific. This
            # will be later required in the prediction stage.
            required_size = len(corpus_pandas.index)
            generic_pandas = pd.read_csv(curr_dir + generic_corpus_path, encoding='utf-8', sep='*')
            if len(corpus_pandas.index) > len(generic_pandas):
                required_size = len(generic_pandas.index)
                
            new_corpus_pandas = new_pandas_generator(corpus_pandas[query_or_answer].sample(n=required_size), np.array([corpus]*required_size))
            new_generic_pandas = new_pandas_generator(generic_pandas['query'].sample(n=required_size), np.array(['generic'] * required_size))
            new_pandas = pd.concat([new_corpus_pandas, new_generic_pandas])
            vectorizer = CountVectorizer(encoding='utf-8', ngram_range=(1,1), tokenizer=TweetTokenizer().tokenize)
            classifier = LinearSVC()
            model_training(new_pandas[query_or_answer], new_pandas['label'], classifier, vectorizer, corpus + '_generic', query_or_answer)


def predict(corpora_dict: dict, query: str, query_or_answer: str) -> list:

    """
    This function receives a query and a dictionary of corpora and uses that information to get a prediction to which
    labels the query could have considering the training that the system has. These predictions take into consideration
    the hierarchy of the corpus and whether they are specific or generic. Regarding the hierarchy, the query is only
    classified with the bottom layers of the hierarchy if it comes from a certain path. Regarding the specificy, the
    query is only classified with a specific corpus if it is find that that corpus is relevant to said query.

    :param corpora_dict: dictionary containing all the relevant information of the corpus to get their models
    and from that get predictions. This dictionary should have the same format as the one returned by the function corpora_xml_reader.
    :param query: a string containing the query for which we wish to retrieve a prediction to.
    :param query_or_answer: A string that indicates if the corpus is of answers or queries.
    :return: a list of predictions for the given query.
    """

    list_of_predictions = []
    for corpus in corpora_dict:
        data = pd.DataFrame([[query]], columns=['query'])
        data = data['query']
        if corpora_dict[corpus]['corpusType'] == 'specific':
            prediction = model_loader(corpus + '_generic', query_or_answer).predict(data)[0]
            # If the corpus in this iteration is specific, but the query is not, we pass this iteration.
            if prediction == 'generic':
                continue
        prediction = model_loader(corpus, query_or_answer).predict(data)[0]
        list_of_predictions.append(prediction)
        rules_result = rules(query, prediction)
        if rules_result is not None:
            list_of_predictions.append(rules_result)
        if 'subcorpus' in corpora_dict[corpus]:
            for subCorpus in corpora_dict[corpus]['subcorpus']:
                subCorpus = corpora_dict[corpus]['subcorpus'][subCorpus]
                if prediction == subCorpus['parentLabel']:
                    # recursively get predictions for all the subcorpus of the current corpus.
                    list_of_predictions += predict({subCorpus['name']: subCorpus}, query, query_or_answer)
        if 'sublabel' in corpora_dict[corpus]:
            file_name = curr_dir + 'models/' + query_or_answer + '/' + prediction + '_model.sav'
            # This cycle gets the models and predictions of all the sublabels until there are no more levels of labels.
            while os.path.isfile(file_name):
                prediction = model_loader(prediction, query_or_answer).predict(data)[0]
                list_of_predictions.append(prediction)
                file_name = curr_dir + 'models/' + query_or_answer + '/' + prediction

    return list_of_predictions


def rules(query: str, previous_prediction: str) -> None or str:

    """
    This function represents a rule-based classifier for sub-classification of questions. It receives a query to predict,
    a previous prediction to verify whether it is a QUESTION, and returns None if it does not find a prediction or a
    string containing a prediction if it finds one.

    :param query: a string containing the query for which we wish to retrieve a prediction to.
    :param previous_prediction: for the case of hierarchy we need to know if the string has already been classified with
    a higher level of the hierarchy to know if it can be classified with a lower one.
    :return: a prediction or none if it does not find a prediction.
    """

    if previous_prediction != 'QUESTION' or ' ' not in query:
        return

    wh_questions_file = open(curr_dir + 'WH_QUESTIONS.txt', 'r')
    list_questions_file = open(curr_dir + 'LIST_QUESTIONS.txt', 'r')
    wh_list = [s.rstrip() for s in list(wh_questions_file)]
    list_list = [s.rstrip() for s in list(list_questions_file)]

    tagger = treetaggerwrapper.TreeTagger(TAGPARFILE=curr_dir + 'resources/TREETAGGER/lib/portuguese.par', TAGDIR=curr_dir + 'resources/TREETAGGER/')
    tags = tagger.tag_text(query)

    if query.lower().split(' ')[0] in wh_list \
            or query.lower().split(' ')[0] + ' ' + query.lower().split(' ')[1] in wh_list:
        return 'WH_QUESTION'

    elif query.lower().split(' ')[0] in list_list:
        index = 1
        if query.lower().split(' ')[1] == 'o' \
                or query.lower().split(' ')[1] == 'a' \
                or query.lower().split(' ')[1] == 'com':
            index = 2
        if tags[index].split('\t')[1] == 'Z' \
                or query.lower().split(' ')[1] == 'um' \
                or query.lower().split(' ')[1] == 'uma':
            return 'LIST_QUESTION'

    elif 'ou' in query:
        return 'OR_QUESTION'




