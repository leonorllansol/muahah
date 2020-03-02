from nltk.stem import WordNetLemmatizer

class Normalizer:
    def applyNormalizations(self, text, normalizers):
        normalized = text
        for normalizer in normalizers:
            normalized = normalizer.normalize(normalized)
        return normalized

class EnglishLemmatizer(Normalizer):
    def __init__(self):
        self.wnl = WordNetLemmatizer()

    def normalize(self, text):
        words = text.split()
        for word in words:
            word = self.wnl.lemmatize(word)
        return " ".join(words)
