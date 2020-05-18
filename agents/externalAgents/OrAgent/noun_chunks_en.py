import spacy
import string
nlp = spacy.load("en_core_web_sm")

def noun_chunks(obj):
    """
    Detect base noun phrases from a dependency parse. Works on both Doc and Span.
    """
    labels = [
        "nsubj",
        "dobj",
        "nsubjpass",
        "pcomp",
        "pobj",
        "dative",
        "appos",
        "attr",
        "ROOT",
    ]
    doc = obj.doc  # Ensure works on both Doc and Span.
    np_deps = [doc.vocab.strings.add(label) for label in labels]
    print(np_deps)
    conj = doc.vocab.strings.add("conj")
    np_label = doc.vocab.strings.add("NP")
    seen = set()
    for i, word in enumerate(obj):
        print(word, word.i)
        if word.pos_ not in ("NOUN", "PROPN", "PRON"):
            continue
        # Prevent nested chunks from being produced
        if word.i in seen:
            continue
        if word.dep in np_deps:
            if any(w.i in seen for w in word.subtree):
                continue
            seen.update(j for j in range(word.left_edge.i, word.i + 1))
            yield word.left_edge.i, word.i + 1, np_label
        elif word.dep == conj:
            head = word.head
            while head.dep == conj and head.head.i < head.i:
                head = head.head
            # If the head is an NP, and we're coordinated to it, we're an NP
            if head.dep in np_deps:
                if any(w.i in seen for w in word.subtree):
                    continue
                seen.update(j for j in range(word.left_edge.i, word.i + 1))
                yield word.left_edge.i, word.i + 1, np_label
                
sentence = "The dog played with the cat."
doc = nlp(sentence)

sentence = sentence.translate(str.maketrans('', '', string.punctuation))
sentence = sentence.split()

chunks = noun_chunks(doc)
noun_chunks = []
for i1, i2, label in chunks:
    s = ""
    for i in range(i1, i2):
        s += sentence[i] + " "
    s = s[:-1]
    noun_chunks.append(s)
print(noun_chunks)
