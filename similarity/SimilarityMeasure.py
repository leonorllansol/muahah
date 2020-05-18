import nltk
import re, math
from collections import Counter

WORD = re.compile(r'\w+')

class SimilarityMeasure:
    def __init__(self, weight):
        self.weight = weight

    def getWeight(self):
        return self.weight

class Jaccard(SimilarityMeasure):
    def distance(self, str1, str2):
        return nltk.jaccard_distance(set(str1), set(str2))

    def finalScore(self, dic):
        c = min(dic, key=dic.get)
        return c.getAnswer(), dic[c]

class Dice(SimilarityMeasure):
    def distance(self, str1, str2):
        set_1 = set(str1)
        set_2 = set(str2)
        overlap = len(set_1 & set_2)
        return 2 * overlap / (len(set_1) + len(set_2))

    def finalScore(self, dic):
        c = max(dic, key=dic.get)
        return c.getAnswer(), dic[c]

class EditDistance(SimilarityMeasure):
    def distance(self, str1, str2):
        return nltk.edit_distance(str1, str2)

    def finalScore(self, dic):
        c = min(dic, key=dic.get)
        return c.getAnswer(), dic[c]

class CosineSimilarity(SimilarityMeasure):

    def distance(self, str1, str2):
        vec1 = self.text_to_vector(str1)
        vec2 = self.text_to_vector(str2)
        return self.get_cosine(vec1,vec2)


    def get_cosine(self, vec1, vec2):
     intersection = set(vec1.keys()) & set(vec2.keys())
     numerator = sum([vec1[x] * vec2[x] for x in intersection])

     sum1 = sum([vec1[x]**2 for x in vec1.keys()])
     sum2 = sum([vec2[x]**2 for x in vec2.keys()])
     denominator = math.sqrt(sum1) * math.sqrt(sum2)

     if not denominator:
        return 0.0
     else:
        return float(numerator) / denominator

    def text_to_vector(self, text):
        words = WORD.findall(text)
        return Counter(words)