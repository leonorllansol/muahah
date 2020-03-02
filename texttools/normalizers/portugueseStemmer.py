'''from .normalizer import Normalizer
from ptstemmer import Stemmer
from ptstemmer.support import PTStemmerUtilities
from ptstemmer.implementations.OrengoStemmer import OrengoStemmer


class PortugueseStemmer(Normalizer):
    def __init__(self):
        stemmer = OrengoStemmer()
        stemmer.enableCaching(1000)
        #Optional
        stemmer.ignore(PTStemmerUtilities.fileToSet("./resources/namedEntities/namedEntities.txt"))

    def normalize(self, text):
        separator = " "
        return separator.join(stemmer.getPhraseStems(text))
'''
import nltk
#nltk.download()
from .normalizer import Normalizer

class PortugueseStemmer(Normalizer):
    def __init__(self):
        self.stemmer = nltk.stem.RSLPStemmer()

    def normalize(self, text):
        words = text.split()
        for word in words:
            #print("before:" + word)
            word = self.stemmer.stem(word)
            #print("after:" + word)
        return " ".join(words)
