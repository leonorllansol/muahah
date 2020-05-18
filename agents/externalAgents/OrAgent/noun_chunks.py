import spacy
import string

nlp = spacy.load("pt_core_news_sm")

def noun_chunks(obj):
    combo1 = ["NOUN"]
    combo11 = ["ADP", "NOUN"]
    combo2 = ["DET", "NOUN"]
    combo3 = ["NOUN", "ADJ"]
    combo31 = ["ADP", "NOUN", "ADJ"]
    combo4 = ["DET", "NOUN", "ADJ"]
    combo5 = ["PRON"]
    combo51 = ["ADP", "PRON"]
    combo6 = ["PROPN"]
    combo61 = ["ADP","PROPN"]
    combo7 = ["ADJ"]
    
    chunks = []
    
    d = []
    for i, word in enumerate(obj):
        d.append(word.pos_)
        
    #print(d)
    
    for i in range(len(d)-2):
        for combo in [combo31, combo4]:
            if not find_all(chunks, i, 3):
                temp = [d[i],d[i+1],d[i+2]]
                if temp == combo:
                    c = [i, i+1, i+2]
                    chunks.append(c)
                
    for i in range(len(d)-1):
        for combo in [combo11, combo2, combo3, combo51, combo61]:
            if not find_all(chunks, i, 2):
                temp = [d[i],d[i+1]]
                if temp == combo:
                    c = [i, i+1]
                    chunks.append(c)
             
    for i in range(len(d)):
        for combo in [combo1, combo5, combo6, combo7]:
            if not find_all(chunks, i, 1):
                if [d[i]] == combo:
                    c = [i]
                    chunks.append(c)
                
    return chunks
      
def find_index(chunks, i):
    for c in chunks:
        if i in c:
            return True
    return False

def find_all(chunks, i, n):
    for j in range(i, i+n):
        if find_index(chunks, i):
            return True
    return False

def get_noun_phrases(sentence):
    doc = nlp(sentence)
    # strip punctuation
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
    sentence = sentence.split()
    chunks = noun_chunks(doc)
    return chunks_to_words(chunks, sentence)
    
def chunks_to_words(chunks, sentence):
    chunks_to_words = []
    for c in chunks:
        s = ""
        for i in c:
            s += sentence[i] + " "
        s = s[:-1]
        chunks_to_words.append(s)
    return chunks_to_words
    
def get_noun_phrase_before_or(sentence):
    doc = nlp(sentence)
    # strip punctuation
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
    sentence = sentence.split()
    chunks = noun_chunks(doc)
    
    or_index = sentence.index("ou")
    for chunk in chunks:
        if chunk[-1] == or_index - 1:
            return chunks_to_words([chunk], sentence)
    return ""

def get_noun_phrase_after_or(sentence):
    doc = nlp(sentence)
    # strip punctuation
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
    sentence = sentence.split()
    chunks = noun_chunks(doc)
    
    or_index = sentence.index("ou")
    for chunk in chunks:
        if chunk[0] == or_index + 1:
            return chunks_to_words([chunk], sentence)
    return ""

