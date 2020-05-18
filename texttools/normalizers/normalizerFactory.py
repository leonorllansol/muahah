from .simpleNormalizer import SimpleNormalizer
from .portugueseStemmer import PortugueseStemmer
from .normalizer import EnglishLemmatizer

def createNormalizers(normalizersStrings):
    normalizers = []
    for norm in normalizersStrings:
        if norm == "RemoveDiacriticalMarks":
            normalizers.append(SimpleNormalizer())
        elif norm == "PortugueseStemmer":
            normalizers.append(PortugueseStemmer())
        elif norm == "EnglishLemmatizer":
            normalizers.append(EnglishLemmatizer())
    return normalizers
