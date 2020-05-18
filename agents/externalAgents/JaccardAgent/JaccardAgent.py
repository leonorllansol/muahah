

class JaccardAgent:
    def __init__(self,configs,indexval=''):
        self.agentName = self.__class__.__name__
        self.questionSimValue = float(configs['questionSimValue'])
        self.answerSimValue = float(configs['answerSimValue'])
        self.normalizeUserInput = True
        self.stopwordsPath = configs['stopwords']



    def requestAnswer(self,userInput,candidates):

        userInputWords = self.getWordSet(userInput)
        userInputWords_WoStopwords = self.getStringListWithoutStopWords(userInputWords)
        bestPairs = [candidates[0]]

        for c in candidates:
            questionWords = self.getWordSet(c.getNormalizedQuestion())
            answerWords = self.getWordSet(c.getNormalizedAnswer())

            questionWords_WoStopwords = self.getStringListWithoutStopWords(questionWords)
            answerWords_WoStopwords = self.getStringListWithoutStopWords(answerWords)

            #questionScore = len(userInputWords.intersection(questionWords)) / len(userInputWords.union(questionWords))
            #answerScore = len(userInputWords.intersection(answerWords)) / len(userInputWords.union(answerWords))
            try:
                questionScore = len(userInputWords_WoStopwords.intersection(questionWords_WoStopwords)) / len(userInputWords_WoStopwords.union(questionWords_WoStopwords))
                answerScore = len(userInputWords_WoStopwords.intersection(answerWords_WoStopwords)) / len(userInputWords_WoStopwords.union(answerWords_WoStopwords))
            except ZeroDivisionError:
                questionScore = 0
                answerScore = 0


            finalScore = self.getFinalScore(questionScore,answerScore)
            c.addScore(self.agentName,finalScore)

            try:
                if(c.getAnswer()[len(c.getAnswer())-1] != '?' and c != bestPairs[0]):
                    if(c.getScoreByEvaluator(self.agentName) > bestPairs[0].getScoreByEvaluator(self.agentName)):
                        bestPairs = [c]
                    elif(c.getScoreByEvaluator(self.agentName) == bestPairs[0].getScoreByEvaluator(self.agentName)):
                        bestPairs.append(c)
            except IndexError:
                pass
        
        return bestPairs



    def getWordSet(self,input):
        #tokenizedInput = re.sub(r'\W+',' ',input).lower()
        #wordSet = set(tokenizedInput.split())
        wordSet = set(input.split())
        return wordSet

    def getFinalScore(self,questionScore,answerScore):
        return questionScore * self.questionSimValue + answerScore * self.answerSimValue



    def getStringListWithoutStopWords(self,tokenizedQuestion):
        stopWords = self.getStopWords()
        stringList = []
        for word in tokenizedQuestion:
            if not word in stopWords:
                stringList.append(word)
        return set(stringList)

    def getStopWords(self):
        path = self.stopwordsPath
        f = open(path, 'r', encoding='latin-1')
        stopwords = []
        lines = f.readlines()[16:]
        for line in lines:
            stopwords.append(line.split()[0])
        return stopwords
