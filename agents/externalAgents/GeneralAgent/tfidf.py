from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import re, copy

"""
:param swPath - stopwords path
:param corpus - list of all questions
:return tfidf_by_sentence - dictionary with tfidf scores by sentence
"""
def getTfIdfScore(swPath, corpus):
    temp_corpus = copy.deepcopy(corpus)
    # remove stopwords
    for i in range(len(corpus)):
        temp_corpus[i] = getStringWithoutStopWords(getWordSet(corpus[i]), swPath)
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(temp_corpus)
    tfidf_by_sentence = {}
    for i in range(len(corpus)):
        first_vector_tfidfvectorizer= X[i]
        df = pd.DataFrame(first_vector_tfidfvectorizer.T.todense(), index=vectorizer.get_feature_names(), columns=["tfidf"])
        d = df.sort_values(by=["tfidf"],ascending=False).to_dict()['tfidf']
        tfidf_by_sentence[corpus[i]] = d
    return tfidf_by_sentence


def getStringWithoutStopWords(tokenizedQuestion, swPath):
    stopWords = getStopWords(swPath)
    stringList = []
    for word in tokenizedQuestion:
        if not word in stopWords:
            stringList.append(word)
    sep = " "
    return sep.join(stringList)

def getStopWords(swPath):
    f = open(swPath, 'r', encoding='latin-1')
    stopwords = []
    lines = f.readlines()[16:]
    for line in lines:
        stopwords.append(line.split()[0])
    return stopwords

def getWordSet(input):
    tokenizedInput = re.sub(r'\W+',' ',input).lower()
    wordSet = set(tokenizedInput.split())
    #wordSet = set(input.split())
    return wordSet
