from .normalizer import Normalizer
import configsparser

class SimpleNormalizer(Normalizer):
    #remove puncts , upper case to lower case
    def normalize(self, text):
        normalized = text.lower()

        path = configsparser.getNormalizersPath()
        f = open(path, 'r')
        puncts = f.readlines()
        puncts[-1] = puncts[-1].strip()
        puncts = puncts[0].split(" ")
        
        for sym in puncts:
            normalized = normalized.replace(sym, '')
        return normalized
