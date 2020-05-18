import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter, defaultdict

class KMeansAgent:
    def __init__(self,configs):
        self.agentName = self.__class__.__name__
        self.normalizeUserInput = True


    def requestAnswer(self,userInput,candidates):
        
        firstCandidate = candidates.pop(0).getNormalizedAnswer()
        answers = [firstCandidate]
        word_set = set(firstCandidate.split())

        #Populate word_set
        for candidate in candidates:
            answers.append(candidate.getNormalizedAnswer())
            word_set = word_set.union(set(candidate.getNormalizedAnswer().split()))

        '''

        #create dicts and populate them

        dictWords = {}

        for answer in answers:
            dictWords[answer] = dict.fromkeys(word_set,0)
            for word in answer.split():
                dictWords[answer][word] += 1

        dictTfs = {}

        for answer in answers:
            dictTfs[answer] = compute_tf(dictWords[answer],answer.split())
        

        idf = compute_idf(dictWords)


        dictTfIdfs = {}

        for answer in answers:
            dictTfIdfs[answer] = compute_tf_idf(dictTfs[answer],idf)

        '''

        tfidf_vectorizer = TfidfVectorizer()
        tfidf = tfidf_vectorizer.fit_transform(answers)

        kmeans = KMeans(n_clusters=500).fit(tfidf)

        clusterNum = kmeans.predict(tfidf_vectorizer.transform(answers))

        counter = Counter(kmeans.labels_)

        clusDict = {}
        for i in range(len(answers)):
            if(clusterNum[i] in clusDict.keys()):
                clusDict[clusterNum[i]].append(answers[i])
            else:
                clusDict[clusterNum[i]] = [answers[i]]
            #print(answers[i],clusterNum[i])

        #for k, v in sorted(clusDict.items()):
        #    print(k, v)

        
        #maxClusterSize = sorted( ((v,k) for k,v in counter.items()), reverse=True)[0][0]


        clusterSentenceFreq = {}

        for k in clusDict.keys():
            for e in clusDict[k]:
                if(e in clusterSentenceFreq.keys()):
                    clusterSentenceFreq[e] += 1
                else:
                    clusterSentenceFreq[e] = 1

        bestPair = candidates[0]

        for i in range(len(candidates)):
            #score = clusterSentenceFreq[candidates[i].getNormalizedAnswer()]/maxClusterSize
            print(clusterSentenceFreq[candidates[i].getNormalizedAnswer()])
            print(len(clusDict[clusterNum[i]]))
            score = clusterSentenceFreq[candidates[i].getNormalizedAnswer()]/len(clusDict[clusterNum[i]])
            candidates[i].addScore(self.agentName,score)

            if(candidates[i].getScoreByEvaluator(self.agentName) > bestPair.getScoreByEvaluator(self.agentName)):
                bestPair = candidates[i]
                print(bestPair.getAnswer(), i, score)

        return bestPair.getAnswer()

        

        



        return 'No answer found'



def compute_tf(word_dict, l):
    tf = {}
    sum_nk = len(l)
    for word, count in word_dict.items():
        tf[word] = count/sum_nk
    return tf



def compute_idf(word_dicts):
    keys = list(word_dicts.keys())
    n = len(keys)
    idf = dict.fromkeys(word_dicts[keys[0]].keys(), 0)
    for k in keys:
        for word, count in word_dicts[k].items():
            if count > 0:
                idf[word] += 1
    
    for word, v in idf.items():
        idf[word] = math.log(n / float(v))
    return idf


def compute_tf_idf(tf, idf):
    tf_idf = dict.fromkeys(tf.keys(), 0)
    for word, v in tf.items():
        tf_idf[word] = v * idf[word]
    return tf_idf
    