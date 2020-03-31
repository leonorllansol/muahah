import re, os, sys, inspect
from texttools import stopwords
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
four_up =  os.path.abspath(os.path.join(__file__ ,"../../../.."))

sys.path.insert(0, parent_dir)
sys.path.append(current_dir)
import classification
import configsparser
import string
from nltk.metrics.distance import jaccard_distance
from nltk.corpus import wordnet
import nltk

class AMAAgent:
    def __init__(self,configs):
        self.agentName = self.__class__.__name__
        self.corpusPath = configs['corpusPath']
        self.indexPath = configs['indexPath']
        self.threshold = float(configs['threshold'])
        self.stopwordsPath = configs['stopwords']
        self.context = []
        self.corpora_dict = configsparser.getCorporaProperties(four_up + '/config/corpora_config.xml')


    def requestAnswer(self,query,candidates, query_labels, AMA_labels):


        found_AMA_label = False
        query_AMA_label = ""

        print(query_labels)
        for label in query_labels:
            if label in AMA_labels:
                found_AMA_label = True
                query_AMA_label = label
                self.context.append(label)

        if not found_AMA_label:
            return 'Não sei responder a isso'

        if(len(candidates) > 0):
            bestPair = candidates[0]

            bestPairLst = [bestPair]

            for c in candidates:

                # 1 semelhança entre pergunta e perguntas do corpus
                # 2 se há várias semelhantes, escolher a resposta com a label da pergunta anterior
                querySet = self.getWordSet(query)
                querySetNoStopwords = self.getStringListWithoutStopWords(querySet)


                candidateSet = self.getWordSet(c.getNormalizedQuestion())
                candidateSetNoStopwords = self.getStringListWithoutStopWords(candidateSet)

                # consider stemming and synonyms while calculating difference between two sets
                def setDifferenceWithStemmingAndSynonyms(set1, set2):
                    stemmer = nltk.stem.RSLPStemmer()
                    set1 = list(set1)
                    set2 = list(set2)
                    for word in set1:
                        for i in range(len(set2)):
                            for syn in wordnet.synsets(word, lang='por'):
                                for l in syn.lemmas(lang='por'):
                                    word_stemmed = stemmer.stem(word)
                                    temp_stemmed = stemmer.stem(set2[i])
                                    if stemmer.stem(l.name()) == temp_stemmed:
                                        set2[i] = word
                    set1 = set(set1)
                    set2 = set(set2)
                    return set1 - set2

                # max - len(q) == len(querySetNoStopwords)
                q = querySetNoStopwords - setDifferenceWithStemmingAndSynonyms(querySetNoStopwords, candidateSetNoStopwords)
                d = candidateSetNoStopwords - setDifferenceWithStemmingAndSynonyms(candidateSetNoStopwords, querySetNoStopwords)
                sim_score = len(q)/len(querySetNoStopwords) + len(d)/len(candidateSetNoStopwords)
                print(sim_score, c.getNormalizedQuestion())
                print()

                c.addScore(self.agentName,sim_score)


            # sort candidates in descending order
            candidates.sort(key=lambda x: x.getScoreByEvaluator(self.agentName), reverse=True)

            max_score = candidates[0].getScoreByEvaluator(self.agentName)
            top_candidates= [candidates[0]]
            for i in range(1, len(candidates)):
                if max_score - candidates[i].getScoreByEvaluator(self.agentName) <= 0.50:
                    top_candidates.append(candidates[i])

            if len(self.context) > 1:
                top_candidates_same_label = []
                for c in top_candidates:
                    answer_labels = classification.predict(self.corpora_dict['answer'], c.getAnswer(), 'answer')

                    answer_AMA_label = ""
                    for label in answer_labels:
                        if label in AMA_labels:
                            answer_AMA_label = label
                            break

                    #if query_AMA_label == answer_AMA_label:

                    # - 2 para ir buscar label da pergunta anterior
                    if len(self.context) > 1 and answer_AMA_label == self.context[-2]:
                        top_candidates_same_label.append(c)
                if len(top_candidates_same_label) == 0:
                    return top_candidates[0].getAnswer()
                else:
                    return top_candidates_same_label[0].getAnswer()

            else:
                return top_candidates[0].getAnswer()


                '''
                answer_labels = classification.predict(self.corpora_dict['answer'], c.getAnswer(), 'answer')


                answer_AMA_label = ""
                for label in answer_labels:
                    if label in AMA_labels:
                        answer_AMA_label = label
                        break

                #if query_AMA_label == answer_AMA_label:

                # - 2 para ir buscar label da pergunta anterior
                if len(self.context) > 1 and answer_AMA_label == self.context[-2]:
                    score = 1
                else:
                    score = 0
                if len(self.context) > 1:
                    print(c.getAnswer() + " : " + answer_AMA_label + " : " + self.context[-2] + " : " + str(score))

                # questionWords = self.getWordSet(c.getNormalizedQuestion())
                #
                # questionWords_WoStopwords = self.getStringListWithoutStopWords(questionWords)
                #
                # score = len(userInputWords.intersection(questionWords)) / len(userInputWords.union(questionWords))
                #score = len(userInputWords_WoStopwords.intersection(questionWords_WoStopwords)) / len(userInputWords_WoStopwords.union(questionWords_WoStopwords))
                c.addScore(self.agentName,score)

                if(c.getScoreByEvaluator(self.agentName) > bestPair.getScoreByEvaluator(self.agentName)):
                    bestPair = c'''
        else:
            return 'Não sei responder a isso'

        #if(bestPair.getScoreByEvaluator(self.agentName) > self.threshold):
        return bestPair.getAnswer()
        # else:
        #     return 'Não sei responder a isso'



    def getWordSet(self,input):
        tokenizedInput = re.sub(r'\W+',' ',input).lower()
        wordSet = set(tokenizedInput.split())
        #wordSet = set(input.split())
        return wordSet


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
