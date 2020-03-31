import os
import re
from whoosh.index import create_in, open_dir, EmptyIndexError
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.qparser import QueryParser,OrGroup
from dialog.SimpleQA import SimpleQA
import configsparser





def createIndex(indexPath,corpusPath):
    schema = Schema(question=TEXT(stored=True), answer=TEXT(stored=True), normalizedquestion=TEXT(stored=True), normalizedanswer=TEXT(stored=True), diff=NUMERIC(stored=True))

    if not os.path.exists(indexPath):
        os.mkdir(indexPath)

    index = create_in(indexPath, schema)
    indexWriter = index.writer()
    corpusQAs = subtitleCorpusReader(corpusPath)
    for qa in corpusQAs:
        indexWriter.add_document(question=qa.question, answer=qa.answer, normalizedquestion=qa.normalizedQuestion, normalizedanswer=qa.normalizedAnswer, diff=qa.diff)

    indexWriter.commit()

    return index



def openIndex(indexPath, corpusPath):
    try:
        index = open_dir(indexPath)
        return index
    except EmptyIndexError:
        print("Index for " + str(corpusPath) + " does not exist; creating...")
        index = createIndex(indexPath, corpusPath)
        return index



def generateCandidates(inputQuestion, indexPath=configsparser.getIndexPath(), corpusPath=configsparser.getCorpusPath()):

    hitsPerQuery = int(configsparser.getHitsPerQuery())
    index = openIndex(indexPath, corpusPath)

    searcher = index.searcher()
    docs = searcher.documents()
    parser = QueryParser("normalizedquestion",index.schema,group=OrGroup)
    q = parser.parse(inputQuestion)
    hits = searcher.search(q,limit=hitsPerQuery)
    candidates = candidatesToQA(hits)

    return candidates




def subtitleCorpusReader(corpusPath):

    corpus = open(corpusPath,"r",encoding="utf8")
    lines = corpus.read().splitlines()
    line = 0
    qaList = []
    while(line < len(lines)):
        if(lines[line].strip() == ''):
            line += 1
            continue
        subID = lines[line].split(' - ')[1]
        line += 1

        dialogID = lines[line].split(' - ')[1]
        line += 1

        diff = int(lines[line].split(' - ')[1])
        line += 1

        question = lines[line].split(' - ')[1]
        line += 1

        answer = lines[line].split(' - ')[1]
        line += 1
        while(line < len(lines) - 1 and lines[line+1].split(' - ')[0] != "SubId"):
            answer += '\n'
            answer += lines[line]
            line += 1


        normalizedQuestion = cleanSentence(question)
        normalizedAnswer = cleanSentence(answer)

        qaList.append(SimpleQA(-1,question, normalizedQuestion, answer, normalizedAnswer, diff))

    return qaList


def candidatesToQA(candidates):
    qaList = []
    for c in candidates:
        qaList.append(SimpleQA(-1,c["question"], c["normalizedquestion"], c["answer"], c["normalizedanswer"], c["diff"]))

    return qaList





def cleanSentence(sentence):

    tokens = [x for x in re.split(r'\W+',sentence.lower()) if x != '']
    cleanS = "".join([" "+i for i in tokens]).strip()
    return cleanS



def getSubstringAfterHyphen(temp):
    return temp[temp.index('-') + 2:]
