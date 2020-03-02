import configsparser, conversation
import logging
from dialog.SimpleQA import SimpleQA
from dialog.BasicQA import BasicQA
from operator import itemgetter
from dialog.evaluators import QaScorerFactory
from similarity import SimilarityMeasureFactory
from texttools.normalizers import normalizerFactory
from texttools.normalizers.normalizer import Normalizer
import subprocess

class AbstractAnswerSelection:

    """
    The AbstractAnswerSelection class serves as the base class for all AnswerSelection classes
    """


    def __init__(self):
        self.normalizers = normalizerFactory.createNormalizers(configsparser.getNormalizers())
        self.evaluators = QaScorerFactory.createQaScorers(configsparser.getEvaluators())
        self.similarityMeasures = SimilarityMeasureFactory.createSimilarityMeasures(configsparser.getSimilarityMeasure())
        self.conversation = conversation.Conversation()

    def provideAnswer(self, query):
        query_normalized = Normalizer().applyNormalizations(query, self.normalizers)

        list_args = ["java", "LuceneWrapper", "-2", configsparser.getCorpusPath(), query_normalized, configsparser.getLanguage(), configsparser.getIndexPath(), configsparser.getHitsPerQuery(), configsparser.getDbPath()]
        sp1 = subprocess.Popen(list_args,shell=False)
        exitCode = sp1.wait()

        luceneResults = open('luceneresults.txt', 'r')

        logging.info("Normalized query: " + query_normalized)
        lines = luceneResults.readlines()
        strippedLines = []
        for line in lines:
            strippedLines.append(line.strip('\n'))

        luceneResults.close()

        candidates = getCandidatesFromLuceneResults(query, strippedLines)

        logging.info("Candidates:")
        for c in candidates:
            logging.info(c.textual())
        logging.info("\n")

        return self.provideAnswerWithCandidates(query, query_normalized, candidates)

    def provideAnswerWithCandidates(self, query, query_normalized, candidates):
        if len(candidates) == 0:
            return configsparser.getNoAnswerMessage()
        else:
            exactMatches = findExactMatches(query_normalized, candidates)

            if len(exactMatches) == 0:
                print("404 Exact Match Not Found")
                answer = self.chooseAnswer(query_normalized, candidates)

            elif len(exactMatches) == 1:
                print("One Exact Match Found")
                answer = exactMatches[0].getAnswer()

            else:
                print("Several Exact Matches Found")
                answer = self.chooseAnswer(query_normalized, candidates)

            answer_normalized = Normalizer().applyNormalizations(answer, self.normalizers)
            self.conversation.addQA(BasicQA(query, answer, query_normalized, answer_normalized))
            return answer

    def getConversation(self):
        return self.conversation

    def getEvaluatorsScores(self, query, candidates):
        answers_per_evaluator = []
        for evaluator in self.evaluators:
            #logging.info("evaluator: " + evaluator)
            highest_scored_candidates = []
            for similarityMeasure in self.similarityMeasures:
                highest_candidate, highest_score = evaluator.score(similarityMeasure, query, candidates, self.conversation)
                highest_scored_candidates.append((highest_candidate, similarityMeasure.getWeight()))
                logging.info('\n')
                logging.info("score:")
                logging.info(highest_score)
                logging.info('\n')

            #get answer with highest score with evaluator by weighting all similarity measures
            final_sm_candidate = getFinalCandidate(highest_scored_candidates)
            answers_per_evaluator.append((final_sm_candidate, evaluator.getWeight(),evaluator.__class__.__name__))
        return answers_per_evaluator




class HighestWeightedScoreSelection(AbstractAnswerSelection):
    def chooseAnswer(self, query, candidates):
        self.answers_per_evaluator = self.getEvaluatorsScores(query, candidates)
        logging.info("ANSWERS PER EVALUATOR")
        logging.info(self.answers_per_evaluator)
        final_candidate = max(self.answers_per_evaluator,key=itemgetter(1))[0]
        logging.info("ANSWER: " + final_candidate)
        return final_candidate

''' # learning #
class MostVotedSelection(AbstractAnswerSelection):
    def chooseAnswer(self, query, candidates):
        self.answers_per_evaluator, candidates = self.getEvaluatorsScores(query, candidates)
        #get answer with highest score by weighting all evaluators
        final_candidate = getFinalCandidate(self.answers_per_evaluator)
        logging.info("ANSWER: " + final_candidate)
        return final_candidate
'''
# --- AUXILIAR ---


class MultipleAnswerSelection(AbstractAnswerSelection):

    #overriding original method
    def provideAnswerWithCandidates(self, query, query_normalized, candidates):
        answers_per_evaluator = self.getEvaluatorsAnswersDict(query_normalized,candidates)
        return answers_per_evaluator


    def getEvaluatorsAnswersDict(self, query, candidates):
        answers_per_evaluator = {}
        for evaluator in self.evaluators:
            #logging.info("evaluator: " + evaluator)
            highest_scored_candidates = []
            for similarityMeasure in self.similarityMeasures:
                try:
                    highest_candidate, highest_score = evaluator.score(similarityMeasure, query, candidates, self.conversation)
                    highest_scored_candidates.append((highest_candidate, similarityMeasure.getWeight()))
                    logging.info('\n')
                    logging.info("score:")
                    logging.info(highest_score)
                    logging.info('\n')

                except ValueError:
                    highest_scored_candidates.append((configsparser.getNoAnswerMessage(), similarityMeasure.getWeight()))
                    
            #get answer with highest score with evaluator by weighting all similarity measures
            final_sm_candidate = getFinalCandidate(highest_scored_candidates)
            answers_per_evaluator[evaluator.__class__.__name__] = final_sm_candidate
        return answers_per_evaluator



def getCandidatesFromLuceneResults(query, lines):
    candidates = []
    for i in range(0, len(lines), 6):
        previousQA = lines[i]
        question = lines[i+1]
        answer = lines[i+2]
        normalizedQuestion = lines[i+3]
        normalizedAnswer = lines[i+4]
        diff = lines[i+5]
        qa = SimpleQA(previousQA, question, normalizedQuestion, answer, normalizedAnswer, diff)
        candidates.append(qa)
    return candidates

def findExactMatches(query, candidates):
    exactMatches = []
    for candidate in candidates:
        if query == candidate.getNormalizedQuestion()[:-1]:
            exactMatches.append(candidate)
    return exactMatches

def getFinalCandidate(weightedCandidates):
    dic = {}
    for (candidate, weight) in weightedCandidates:
        if not candidate in dic:
            dic[candidate] = int(weight)
        else:
            dic[candidate] += int(weight)

    logging.info("weightedCandidates:")
    logging.info(weightedCandidates)
    logging.info("\n")
    logging.info(dic)
    logging.info('\n')

    return max(dic, key=dic.get)
