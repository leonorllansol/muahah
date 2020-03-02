#pip install stanfordcorenlp
from stanfordcorenlp import StanfordCoreNLP

class TextAnalyzer:
    def __init__(self, host='http://localhost', port=9000):
        self.nlp = StanfordCoreNLP(host, port=port, timeout=30000)
        self.props = {
            'annotators': 'tokenize,ssplit,pos,lemma,ner,parse,depparse,dcoref,relation',
            'pipelineLanguage': 'en',
            'outputFormat': 'json'
        }

    def analyze(self, text):
        self.annotate(text)
        #TODO

    def annotate(self, sentence):
        return json.loads(self.nlp.annotate(sentence, properties=self.props))
