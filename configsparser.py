import re, os, csv
from xml.dom import minidom
from sklearn.svm import LinearSVC, SVC, NuSVC
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier, RadiusNeighborsClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, BaggingClassifier, ExtraTreesClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.naive_bayes import GaussianNB, BernoulliNB, MultinomialNB, ComplementNB
from nltk import TweetTokenizer
from plug_and_play import file_parsing
# parse an xml file by name
mydoc = minidom.parse('config/config.xml')
curr_dir = os.path.dirname(os.path.abspath(__file__))


def getSimilarityMeasure():
    similarityMeasures = mydoc.getElementsByTagName('similarityMeasure')
    elems = []
    weights = []
    for elem in similarityMeasures:
        elems.append(elem.attributes['name'].value)
        weights.append(elem.attributes['weight'].value)
    return elems, weights

def getEvaluators():
    criteria = mydoc.getElementsByTagName('criterion')
    elems = []
    for elem in criteria:
        if elem.attributes['weight'].value != '0':
            if elem.attributes['name'].value == 'SimpleConversationContext':
                elems.append((elem.attributes['name'].value, elem.attributes['weight'].value, elem.attributes['nPreviousInteractions'].value))
            else:
                elems.append((elem.attributes['name'].value, elem.attributes['weight'].value, '0'))
    return elems

def getNormalizers():
    normalizersStrings = mydoc.getElementsByTagName('normalizers')[0]
    return (normalizersStrings.firstChild.data).split(',')

def getDbPath():
    dbPath = mydoc.getElementsByTagName('dbPath')[0]
    return dbPath.firstChild.data

def getNoAnswerMessage():
    language = getLanguage()
    if language == 'english':
        noAnswerMessage = mydoc.getElementsByTagName('noAnswerFoundEN')[0]
    elif language == 'portuguese':
        noAnswerMessage = mydoc.getElementsByTagName('noAnswerFoundPT')[0]
    return noAnswerMessage.firstChild.data

def getHitsPerQuery():
    hitsPerQuery = mydoc.getElementsByTagName('hitsPerQuery')[0]
    return hitsPerQuery.firstChild.data

def usePreviouslyCreatedIndex():
    usePreviouslyCreatedIndex = mydoc.getElementsByTagName('usePreviouslyCreatedIndex')[0]
    if(usePreviouslyCreatedIndex.firstChild.data == 'true'):
        return True
    else:
        return False


def getNormalizersPath():
    normalizerPath = mydoc.getElementsByTagName('normalizersPath')[0]
    return normalizerPath.firstChild.data

def getExternalAgentsPath():
    externalAgentsPath = mydoc.getElementsByTagName('externalAgentsPath')[0]
    return externalAgentsPath.firstChild.data

def getLanguage():
    language = mydoc.getElementsByTagName('language')[0]
    return language.firstChild.data

def getIndexPath():
    indexPath = mydoc.getElementsByTagName('indexPath')[0]
    return indexPath.firstChild.data

def getCorpusPath():
    corpusPath = mydoc.getElementsByTagName('corpusPath')[0]
    return corpusPath.firstChild.data

def getStopWordsPath():
    stopWordsPath = mydoc.getElementsByTagName('stopwords')[0]
    return stopWordsPath.firstChild.data

def getDefaultAgentsMode():
    defaultAgentsMode = mydoc.getElementsByTagName('defaultAgentsMode')[0]
    return defaultAgentsMode.firstChild.data


def getDecisionMethodsWeights():
    methods = mydoc.getElementsByTagName('decisionMethod')
    elems = {}
    for elem in methods:
        if elem.attributes['weight'].value != '0':
            elems[elem.attributes['name'].value] = int(elem.attributes['weight'].value)
        else:
            elems[elem.attributes['name'].value] = 0
    return elems


def getActiveAgents():
    agents = mydoc.getElementsByTagName('agent')
    elems = []
    for elem in agents:
        if elem.attributes['active'].value != '0':
            elems.append(elem.attributes['name'].value)
    return elems


def getSequentialQuestionTxtPath():
    questionTxtFile = mydoc.getElementsByTagName('questionTxtFile')[0]
    return questionTxtFile.firstChild.data

def getSequentialTargetTxtPath():
    sequentialTargetTxtFile = mydoc.getElementsByTagName('sequentialTargetTxtFile')[0]
    return sequentialTargetTxtFile.firstChild.data

def getAnswerAmount():
    answerAmount = mydoc.getElementsByTagName('answerAmount')[0]
    return int(answerAmount.firstChild.data)


def getInteractionsPath():
    interactionsPath = mydoc.getElementsByTagName('interactions')[0]
    return interactionsPath.firstChild.data

def getLinesPath():
    linesPath = mydoc.getElementsByTagName('lines')[0]
    return linesPath.firstChild.data

def getInputSize():
    inputSize = mydoc.getElementsByTagName('inputSize')[0]
    return int(inputSize.firstChild.data)

def getDecimalPlaces():
    decimalPlaces = mydoc.getElementsByTagName('decimalPlaces')[0]
    return int(decimalPlaces.firstChild.data)

def getEtaFactor():
    etaFactor = mydoc.getElementsByTagName('etaFactor')[0]
    return int(etaFactor.firstChild.data)

def getLearningStrategy():
    learningStrategy = mydoc.getElementsByTagName('strategy')[0]
    return learningStrategy.firstChild.data

def getWeightResults():
    weightResults = mydoc.getElementsByTagName('weightResults')[0]
    weights = eval(weightResults.firstChild.data)
    toDelete = []
    for agent, w in weights.items():
        flag = False
        for elem in getActiveAgents():
            if agent.startswith(elem):
                flag = True
                break
        if not flag:
            toDelete.append(agent)
    for item in toDelete:
        del weights[item]

    return weights

def getInitialWeights():
    initialWeights = mydoc.getElementsByTagName('initialWeights')[0]
    return eval(initialWeights.firstChild.data)


def getPriorities():
    agents = mydoc.getElementsByTagName('agentPriority')
    priorityDoc = {}
    for agent in agents:
        priorityDoc[agent.attributes['name'].value] = int(agent.attributes['priority'].value)
    return priorityDoc

'''Mariana'''
def getSystemProperties(path: str) -> dict:

    """
    This function parses the system config file, processes it and builds a dictionary containing the name of each
    module to rank answers and a bool that is True in case the module is to be used and False otherwise. In the
    module of personal answers it also adds a list with each similarity measure to be used. All these informations are
    extracted from the system config file.

    :param path: string containing the path to the system config file
    :return: a dictionary containing the information in the system config file
    """

    doc = minidom.parse(path)

    system_dict = {}
    regex = re.compile(r'[\n\r\t]')
    system_dict['query_agent'] = eval(regex.sub("", doc.getElementsByTagName('query-agent-label-match')[0].firstChild.nodeValue))
    system_dict['answer_impersonal'] = eval(regex.sub("", doc.getElementsByTagName('answer-classification-impersonal')[0].firstChild.nodeValue))
    system_dict['answer_personal'] = [eval(regex.sub("", doc.getElementsByTagName('answer-classification-personal')[0].firstChild.nodeValue)),]
    system_dict['query_answer'] = eval(regex.sub("", doc.getElementsByTagName('query-answer-label-match')[0].firstChild.nodeValue))
    if system_dict['answer_personal'][0]:
        if doc.getElementsByTagName('answer-classification-personal')[0].hasAttribute('sim_measure'):
            sim_measure = regex.sub("", doc.getElementsByTagName('answer-classification-personal')[0].getAttribute('sim_measure'))
            system_dict['answer_personal'] += sim_measure.split('|')
        else:
            system_dict['answer_personal'].append('tfidf_normal')
    return system_dict


def getAgentsProperties(path: str) -> dict:

    """
    This function parses the agents config file, processes it and builds a dictionary containing the agent's path,
    its import path (the package name), the name of the method that the agent has to provide an answer, the
    corpora tags in which it is an expert and finally the answers it gives when it does not find a suitable answer.

    :param path: string containing the path to the agents config file
    :return: a dictionary containing the information in the agents config file
    """

    doc = minidom.parse(path)

    agents_dict = {}
    regex = re.compile(r'[\n\r\t]')
    agents_elements = doc.getElementsByTagName('agent')
    for agent in agents_elements:
        agents_path = curr_dir + '/agents/internalAgents/'
        folder_name = agent.getElementsByTagName('folderName')[0].firstChild.nodeValue
        class_name = agent.getElementsByTagName('classname')[0].firstChild.nodeValue
        method_name = agent.getElementsByTagName('dialogMethod')[0].firstChild.nodeValue
        labels = {}
        escape_sentences = []
        for label in agent.getElementsByTagName('label'):
            try:
                if label.hasAttribute('score'):
                    labels[(regex.sub("", label.firstChild.nodeValue))] = float(label.getAttribute('score'))
                else:
                    labels[(regex.sub("", label.firstChild.nodeValue))] = 1.0
            except ValueError:
                raise Exception('\n\n!!!ERROR!!!\nConfigurations wrong in agents config file. '
                                'The degree attribute must be equal to a string that only contains numbers.')
        for escape_sentence in agent.getElementsByTagName('escapeSentence'):
            escape_sentences.append(escape_sentence.firstChild.nodeValue)
        folder_name = regex.sub("", folder_name)
        agents_path += folder_name
        agents_import = 'agents.internalAgents.' + folder_name + '.' + class_name
        agents_dict[folder_name] = {'path': regex.sub("", agents_path), 'importPath': regex.sub("", agents_import),
                                    'methodName': regex.sub("", method_name), 'labels': labels,
                                    'escapeSentences': escape_sentences}

    agents_elements = doc.getElementsByTagName('externalAgent')
    for agent in agents_elements:
        labels = {}
        for label in agent.getElementsByTagName('label'):
            try:
                if label.hasAttribute('score'):
                    labels[(regex.sub("", label.firstChild.nodeValue))] = float(label.getAttribute('score'))
                else:
                    labels[(regex.sub("", label.firstChild.nodeValue))] = 1.0
            except ValueError:
                raise Exception('\n\n!!!ERROR!!!\nConfigurations wrong in agents config file. '
                                'The degree attribute must be equal to a string that only contains numbers.')

        agents_dict[agent.attributes['name'].value] = {'labels': labels}

    return agents_dict



def getCorporaProperties(path: str) -> dict:

    """
    This function parses the corpora config file, processes it and builds a dictionary containing the information
    in the config file. Some of this information is converted into its final value, such as the vectorizer and
    the classifier which are converted from strings to objects. The nested corpus files are added as a dictionary
    inside the main dictionary under the name (key of the dictionary) of its parent corpus.


    :param path: string containing the path to the corpora coFalsenfig file
    :return: a dictionary containing the information in the corpora config file
    """

    # Auxiliary function that uses the strings of the vectorizer and classifier elements of the xml
    # and its names and params to create an object of one of those types.
    def extract_function(list_of_nodes, name_to_extract):
        if not list_of_nodes.getElementsByTagName(name_to_extract):
            if name_to_extract == 'vectorizer':
                return CountVectorizer(encoding='utf-8', ngram_range=(1,1), tokenizer=TweetTokenizer().tokenize)
            if name_to_extract == 'classifier':
                return LinearSVC()
        function_element = list_of_nodes.getElementsByTagName(name_to_extract)[0]
        function = function_element.getElementsByTagName('name')[0].firstChild.nodeValue + '('
        for el2 in function_element.getElementsByTagName('param'):
            function += el2.firstChild.nodeValue + ','
        if function[-1] == ',':
            function = function[:-1]
        function += ')'
        return eval(function)

    doc = minidom.parse(path)
    corpora = doc.getElementsByTagName('corpus')
    corpora_dict = {}
    corpora_dict['query'] = {}
    corpora_dict['answer'] = {}
    child_corpus_dict = {}
    for corpus in corpora:
        corpus_path = curr_dir + corpus.getElementsByTagName('path')[0].firstChild.nodeValue

        query_or_answer = corpus.getElementsByTagName('name')[0].parentNode
        while query_or_answer.nodeName == 'corpus':
            query_or_answer = query_or_answer.parentNode
        query_or_answer = query_or_answer.nodeName

        # We require a csv file for our program, so if a file .txt is provided, we parse it and create a .csv

        if corpus_path.split('.')[1] == 'txt':
            file_parsing(corpus_path, corpus_path.split('.')[0] + '.csv', query_or_answer)
            corpus_path = corpus_path.split('.')[0] + '.csv'


        corpus_name = corpus.getElementsByTagName('name')[0].firstChild.nodeValue
        corpus_vectorizer = extract_function(corpus, 'vectorizer')
        corpus_classifier = extract_function(corpus, 'classifier')
        parent_label = corpus.getElementsByTagName('parentLabel')

        corpus_type = corpus.getElementsByTagName('corpusType')

        corpus_dict = {'path': corpus_path, 'name': corpus_name, 'vectorizer': corpus_vectorizer,
                       'classifier': corpus_classifier}

        if parent_label:
            corpus_dict['parentLabel'] = parent_label[0].firstChild.nodeValue
        if corpus_type:
            corpus_dict['corpusType'] = corpus_type[0].firstChild.nodeValue
        if not corpus.getElementsByTagName('hierarchyType'):
            pass

        # In here we place in the main dictionary the indication that the corpus at this iteration of the cycle
        # is a subcorpus and that in further processing we are going to need to place it under the key of its parent
        # corpus. We also place the current corpus in an auxiliary dictionary of child corpus's
        elif corpus.getElementsByTagName('hierarchyType')[0].firstChild.nodeValue == 'subcorpus':
            child_corpus_dict[corpus_name] = {'query_or_answer': query_or_answer, 'subcorpus': []}
            for el in corpus.getElementsByTagName('corpus'):
                child_corpus_dict[corpus_name]['subcorpus'].append(el.getElementsByTagName('name')[0].firstChild.nodeValue)
                corpus_dict['subcorpus'] = {}
        # If we have a hierarchy of sublabel, we are going to need the classification needs of the sublabels, in
        # here we create the vectorizer and classifier of the sublabels.
        elif corpus.getElementsByTagName('hierarchyType')[0].firstChild.nodeValue == 'sublabel':
            sub_label_vect = corpus.getElementsByTagName('sublabel')
            corpus_vectorizer = extract_function(sub_label_vect[0], 'vectorizer')
            corpus_classifier = extract_function(sub_label_vect[0], 'classifier')
            corpus_dict['sublabel'] = [corpus_vectorizer, corpus_classifier]
        corpora_dict[query_or_answer][corpus_name] = corpus_dict
    # It is in this cycle that we place the child corpus's dictionary under the key of their parent corpus.
    for name in child_corpus_dict:
        for name2 in child_corpus_dict[name]['subcorpus']:
            corpora_dict[child_corpus_dict[name]['query_or_answer']][name]['subcorpus'][name2] = corpora_dict[child_corpus_dict[name]['query_or_answer']][name2]
            del corpora_dict[child_corpus_dict[name]['query_or_answer']][name2]
    return corpora_dict
