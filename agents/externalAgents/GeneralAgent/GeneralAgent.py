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
from nltk.metrics.distance import jaccard_distance, edit_distance
from nltk.corpus import wordnet
import nltk
import pandas as pd
import tfidf
class GeneralAgent:
    def __init__(self, configs, i):
        print(configs)
        self.agentName = list(configs['corpusPath'].keys())[i]
        self.corpusPath = list(configs['corpusPath'].values())[i]
        self.indexPath = list(configs['indexPath'].values())[i]
        labelsPath = list(configs['labelsPath'].values())[i]
        self.specific_labels=[]
        for line in open(four_up + "/" + labelsPath).readlines():
            self.specific_labels.append(line.strip('\n').split(","))
        self.threshold = float(configs['threshold'])
        self.stopwordsPath = configs['stopwords']
        self.context = []
        self.corpora_dict = configsparser.getCorporaProperties(four_up + '/config/corpora_config.xml')

        #self.tfidf_scores = tfidf.getTfIdfScore(self.stopwordsPath,list(querySources['query'].values()))

        # self.synonyms = []
        # for line in open(current_dir + "/sinonimos.txt").readlines():
        #     self.synonyms.append(line.strip('\n').split(","))
        # self.acronyms = []
        # for line in open(current_dir + "/acronimos.txt").readlines():
        #     self.acronyms.append(line.strip('\n').split(","))
        #
        # print(self.synonyms)
        self.normalizeUserInput = True

    # def getSynonyms(self,word):
    #     for lst in self.synonyms:
    #         if word in lst:
    #             return list(set(lst)-set(word))
    #     return []
    #
    # def getAcronyms(self,word):
    #     for lst in self.acronyms:
    #         if word in lst:
    #             return list(set(lst)-set(word))
    #     return []

    def requestAnswer(self, query, candidates, query_labels):
        found_specific_label = False
        query_specific_label = ""

        print(query_labels)
        for label in query_labels:
            if label in self.specific_labels:
                found_specific_label = True
                query_specific_label = label
                self.context.append(label)

        # if not found_specific_label:
        #     return 'Não sei responder a isso', "", ""

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

                sim_score = self.getDistance(querySetNoStopwords, candidateSetNoStopwords, c.getQuestion())
                
                # print(sim_score, c.getNormalizedQuestion())
                # print()

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

                    answer_covid_label = ""
                    for label in answer_labels:
                        if label in self.specific_labels:
                            answer_covid_label = label
                            break

                    #if query_specific_label == answer_covid_label:

                    # - 2 para ir buscar label da pergunta anterior
                    if len(self.context) > 1 and answer_covid_label == self.context[-2]:
                        top_candidates_same_label.append(c)
                if len(top_candidates_same_label) == 0:
                    return top_candidates[0].getAnswer(), top_candidates[0].getQuestion()
                else:
                    return top_candidates_same_label[0].getAnswer(), top_candidates_same_label[0].getQuestion()

            else:
                return top_candidates[0].getAnswer(), top_candidates[0].getQuestion()
        else:
            return 'Não sei responder a isso', ""

        return bestPair.getAnswer(), bestPair.getQuestion()


    def getDistance(self, querySetNoStopwords, candidateSetNoStopwords, candidateQuestion):
        q = querySetNoStopwords - self.setDifferenceWithStemmingAndSynonyms(querySetNoStopwords, candidateSetNoStopwords)
        c = candidateSetNoStopwords - self.setDifferenceWithStemmingAndSynonyms(candidateSetNoStopwords, querySetNoStopwords)

        sum_q = len(q)
        # for el in q:
        #     if el in self.tfidf_scores[candidateQuestion]:
        #         sum_q += self.tfidf_scores[candidateQuestion][el]
        sum_c = len(c)
        # for el in c:
        #     if el in self.tfidf_scores[candidateQuestion]:
        #         sum_c += self.tfidf_scores[candidateQuestion][el]
        if len(querySetNoStopwords) == 0 or len(candidateSetNoStopwords) == 0:
            return jaccard_distance(querySetNoStopwords, candidateSetNoStopwords)
        sim_score = sum_q/len(querySetNoStopwords) + sum_c/len(candidateSetNoStopwords)
        return sim_score

    # consider stemming and synonyms while calculating difference between two sets
    # TODO put this on a different class
    def setDifferenceWithStemmingAndSynonyms(self, set1, set2):
        stemmer = nltk.stem.RSLPStemmer()
        set1 = list(set1)
        set2 = list(set2)
        to_remove = []
        for word in set1:
            for i in range(len(set2)):
                if word != set2[i]:
                    # for s in self.getSynonyms(word):
                    #     if set2[i] == s:
                    #         set2[i] = word
                    #         to_remove.append(word)
                    # for a in self.getAcronyms(word):
                    #     if set2[i] == a:
                    #         set2[i] = word
                    for syn in wordnet.synsets(word, lang='por'):
                        for l in syn.lemmas(lang='por'):
                            word_stemmed = stemmer.stem(word)
                            temp_stemmed = stemmer.stem(set2[i])
                            if stemmer.stem(l.name()) == temp_stemmed:
                                set2[i] = word
        for it in to_remove:
            if it in set1:
                set1.remove(it)
            if it in set2:
                set2.remove(it)
        set1 = set(set1)
        set2 = set(set2)
        return set1 - set2

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
