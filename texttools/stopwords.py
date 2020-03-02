import configsparser

def getStringListWithoutStopWords(tokenizedQuestion):
    stopWords = getStopWords()
    stringList = []
    for word in tokenizedQuestion:
        if not word in stopWords:
            stringList.append(word)
    return stringList

def getStopWords():
    path = configsparser.getStopWordsPath()
    f = open(path, 'r', encoding='latin-1')
    stopwords = []
    lines = f.readlines()[16:]
    for line in lines:
        stopwords.append(line.split()[0])
    return stopwords
