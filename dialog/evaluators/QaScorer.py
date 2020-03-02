from texttools import stopwords
import logging
class QaScorer:
    def __init__(self, weight):
        self.weight = weight

    def getWeight(self):
        return self.weight

class AnswerFrequency(QaScorer):
    def score(self, similarityMeasure, query, candidates, conversation):
        dic = {}
        for i in range(0, len(candidates)):
            for j in range(1, len(candidates)):
                c1 = candidates[i]
                c2 = candidates[j]
                score = similarityMeasure.distance(c1.getNormalizedAnswer(), c2.getNormalizedAnswer())

                if not c1 in dic:
                    dic[c1] = score
                else:
                    dic[c1] += score

                if not c2 in dic:
                    dic[c2] = score
                else:
                    dic[c2] += score

                c1.addScore('AnswerFrequency', score)
                c2.addScore('AnswerFrequency', score)

        logging.info("AnswerFrequency")

        return similarityMeasure.finalScore(dic)

class AnswerSimilarityToUserQuestion(QaScorer):
    def score(self, similarityMeasure, query, candidates, conversation):
        dic = {}

        tokenizedQuestion = query.split(" ")
        tokenizedQuestionWithoutStopWords = stopwords.getStringListWithoutStopWords(tokenizedQuestion)

        if len(tokenizedQuestionWithoutStopWords) != 0:
            for candidate in candidates:
                scoreUntokenized = similarityMeasure.distance(query, candidate.getNormalizedAnswer())
                score = similarityMeasure.distance(tokenizedQuestionWithoutStopWords, stopwords.getStringListWithoutStopWords(candidate.getNormalizedAnswer().split(" ")))
                dic[candidate] = score
                candidate.addScore('AnswerSimilarityToUserQuestion', score)
        else:
            for candidate in candidates:
                score = similarityMeasure.distance(query, candidate.getNormalizedAnswer())
                dic[candidate] = score
                candidate.addScore('AnswerSimilarityToUserQuestion', score)

        logging.info("AnswerSimilarityToUserQuestion")
        return similarityMeasure.finalScore(dic)

class QuestionSimilarityToUserQuestion(QaScorer):
    def score(self, similarityMeasure, query, candidates, conversation):
        dic = {}
        for candidate in candidates:
            score = similarityMeasure.distance(query, candidate.getNormalizedQuestion())
            dic[candidate] = score
            candidate.addScore('QuestionSimilarityToUserQuestion', score)
        logging.info("QuestionSimilarityToUserQuestion")
        return similarityMeasure.finalScore(dic)

class SimpleTimeDifference(QaScorer):
    def score(self, similarityMeasure, query, candidates, conversation):
        dic = {}
        for candidate in candidates:
            diff = int(candidate.getDiff())
            if diff == 0:
                score = 1
            elif diff <= 80:
                score = 0.3
            elif diff <= 1000:
                score = 0.9 - (diff/5000)
            else:
                score = 0.7 - (diff/2500.0)
                if score < 0:
                    score = 0
            assert score >= 0
            dic[candidate] = score
            candidate.addScore('SimpleTimeDifference', score)

        logging.info("SimpleTimeDifference")
        return similarityMeasure.finalScore(dic)

class SimpleConversationContext(QaScorer): #TODO
    def __init__(self, weight, nPreviousQa):
        self.nPreviousQa = int(nPreviousQa)
        super().__init__(weight)

    def score(self, similarityMeasure, query, candidates, conversation):
        totalScore = 0
        dic = {}

        for qa in candidates:
            currentQA = qa.getPreviousQA()

            if currentQA != -1:
                for i in range(0, self.nPreviousQa):
                    basicQA = conversation.getNFromLastQA(i)
                    if basicQA == -1:   #index out of range
                        break
                    currentQA = currentQA.getPreviousQA()  ##erro aqui

                    if currentQA == -1:
                        break

                    tokenizedQuestion = basicQA.getNormalizedQuestion().split()
                    tokenizedAnswer = basicQA.getNormalizedAnswer().split()

                    totalScore += similarityMeasure.distance(tokenizedQuestion, currentQA.getNormalizedQuestion().split()) +\
                                    similarityMeasure.distance(tokenizedAnswer, currentQA.getNormalizedAnswer().split())
                score = totalScore / (2 * self.nPreviousQa)
                dic[qa] = score
            else:
                dic[qa] = 0

        logging.info("SimpleConversationContext")
        return similarityMeasure.finalScore(dic)
