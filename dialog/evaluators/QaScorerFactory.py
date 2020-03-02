from .QaScorer import AnswerFrequency, AnswerSimilarityToUserQuestion, QuestionSimilarityToUserQuestion, SimpleTimeDifference, SimpleConversationContext

def createQaScorers(evaluatorsText):
    evaluators = []
    for (evaluator, weight, nPreviousQa) in evaluatorsText:
        if evaluator == "AnswerFrequency":
            evaluators.append(AnswerFrequency(weight))
        elif evaluator == "AnswerSimilarityToUserQuestion":
            evaluators.append(AnswerSimilarityToUserQuestion(weight))
        elif evaluator == "QuestionSimilarityToUserQuestion":
            evaluators.append(QuestionSimilarityToUserQuestion(weight))
        elif evaluator == "SimpleTimeDifference":
            evaluators.append(SimpleTimeDifference(weight))
        elif evaluator == "SimpleConversationContext":
            evaluators.append(SimpleConversationContext(weight, nPreviousQa))
    return evaluators
