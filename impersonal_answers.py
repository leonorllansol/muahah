from xml.dom import minidom
import pickle, re, nltk, time
import pandas as pd
import spacy
from classification import model_training, model_loader
from string import punctuation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from nltk import TweetTokenizer
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
import wikipedia
import urllib.request as urllib2
import warnings
from spacy import tokens
import sklearn


def look_synset_tree(hypernym, hyponym: str) -> bool:

    """
    This function ascertains whether the argument hyponym is an hyponym of the argument hypernym.

    :param hypernym: A list of synsets or a synset containing the hypernym(s) to which we wish to match the hyponym
    :param hyponym: A synset of the hyponym to which we wish to match the hypernym(s)
    :return: True if hyponym is an hyponym of the hypernym(s), False otherwise
    """

    hypernyms = []
    if isinstance(hypernym, list):
        for H in hypernym:
            hypernyms += [i for i in H.closure(lambda s: s.hyponyms())]
        hypernyms = set(hypernyms)
    else:
        hypernyms = set([i for i in hypernym.closure(lambda s: s.hyponyms())])

    return hyponym in hypernyms


def look_synonyms(word1: str, word2: str) -> bool:

    """
    This function ascertains whether its arguments are synonyms of each other.

    :param word1: A word that we wish to know if it is a synonym of word2.
    :param word2: A word that we wish to know if it is a synonym of word1.
    :return: True if word1 and word2 are synonyms. False otherwise.
    """

    s = []

    for syn in wn.synsets(word1, lang='por'):
        for l in syn.lemmas():
            s.append(l.name())

    synset_list = [item for sublist in [wn.synsets(el) for el in s] for item in sublist]

    word2_synsets = wn.synsets(word2, lang='por')
    for el in word2_synsets:
        if el in synset_list:
            return True

    return False


def abbr_rules(query: str, query_label_fine: str, answer_tokenized_no_stopwords: list, answer_tokenized_no_lower: list)\
        -> list:

    """
    This function has a set of rules to look for an abbreviation or expansion in an answer. To find an abbreviation, it
    uses a regular expression. For the expansion, it extracts an abbreviation from the query and then looks for words
    with the same letters as the abbreviation in the answer.

    :param query: A query introduced by the user in the system.
    :param query_label_fine: The fine category of the query introduced by the user according to a model trained with the
    Li & Roth corpus.
    :param answer_tokenized_no_stopwords: The answer of the agent tokenized without any stopwords.
    :param answer_tokenized_no_lower: The answer of the agent tokenized without lowercasing the letters.
    :return: A list containing a classification according to the Li & Roth taxonomy. If a classification is not found,
    an empty list is returned.
    """

    classification = []
    if query_label_fine == 'exp':
        a = answer_tokenized_no_stopwords
        count = 0
        words = []
        abbr = ''
        q = query.split(' ')
        for word in q:
            if (bool(re.match('(?:[a-zA-Z]\.){2,}', word)) or bool(re.match('(?:[A-Z]){2,}', word))):
                abbr = word
        abbr = abbr[:-1]
        prevI = -1
        for i in range(0, len(a)):
            if a[i][0] in abbr:
                if count > 0:
                    if prevI != i - 1:
                        count = 0
                        words = []
                count += 1
                prevI = i
                words.append(a[i])
        if words:
            if words[-1][0] == abbr[-1]:
                classification = ['ABBR', 'exp']
    if query_label_fine == 'abb':
        for word in answer_tokenized_no_lower:
            if (bool(re.match('(?:[a-zA-Z]\.){2,}', word)) or bool(re.match('(?:[A-Z]){2,}', word))):
                classification = ['ABBR', 'abb']
                break
    return classification


def num_rules(query_label_fine: str, answer: str, answer_tokenized: list, doc_answer: spacy.tokens.doc.Doc) -> list:

    """
    This function looks for specific details in an answer to detect if it contains a number. If it is looking for a
    date, it searches for keywords or for a pattern in the answer that indicates that it contains a date; if it is
    looking for a code, the function tries to match it to a regex that represents a portuguese zip code; concerning
    fine categories that indicate a number that might contain an unit, the function searches for words that are units
    using wordnet; finally, if the function cannot find a classification with the previous steps, it searches through
    the PoS tags given by spacy to the different words of the answer to see if any of those tags indicates that one word
    is a number. If it is, a classification with just the coarse category "NUM" is obtained.

    :param query_label_fine: The fine category of the query introduced by the user according to a model trained with the
    Li & Roth corpus.
    :param answer: The answer of one agent to the query inserted by the user.
    :param answer_tokenized: The answer of the agent tokenized.
    :param doc_answer: The answer of the agent on the format of spacy.
    :return: A list containing a classification according to the Li & Roth taxonomy. If a classification is not found,
    an empty list is returned.
    """

    classification = []
    if query_label_fine == 'date':
        months = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro',
                  'novembro', 'dezembro']
        keywords = ['dia', 'mês', 'ontem', 'amanhã', 'anteontem', 'ano', 'mes', 'amanha']
        dias = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'domingo', 'terca', 'sabado',
                'segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira']
        match = re.search(r'(\d+/\d+/\d+)', answer)
        match2 = re.search(r'(\d+-\d+-\d+)', answer)
        match3 = re.search(r'(\d+.\d+.\d+)', answer)
        if match or match2 or match3:
            classification = ['NUM', 'date']
        for word in answer_tokenized:
            if word.lower() in months or word.lower() in keywords or word.lower() in dias:
                classification = ['NUM', 'date']
    elif query_label_fine == 'code':
        match = re.search(r'(\d{4}-\d{3})', answer)
        if match:
            classification = ['NUM', 'code']
    elif query_label_fine == 'volsize' or query_label_fine == 'dist' or query_label_fine == 'weight' or query_label_fine == 'temp' or query_label_fine == 'speed':
        for word in answer_tokenized:
            hyponym = wn.synsets(word, lang='por')
            hypernym = wn.synsets('unidade', lang='por')[-2]
            if len(classification) == 2:
                break
            for h in hyponym:
                if look_synset_tree(hypernym, h):
                    classification = ['NUM', query_label_fine]
                    break
    if not classification:
        for i in range(0, len(doc_answer)):
            if (doc_answer[i].pos_ == 'NUM'):
                classification = ['NUM']
    return classification


def loc_hum_rules(query: str, query_label_coarse: str, ents: tuple, model_coarse: sklearn.pipeline.Pipeline) -> list:

    """
    This function uses spacy's named entity recognizer to extract the entities from an agent's answer. If it finds an
    ORG, a classification of HUM:gr is automatically achieved, otherwise, only the coarse label is found and then
    the model trained with the multieight corpus is used to obtain the fine label, or both in case none is found.

    :param query: The query inserted by the user.
    :param query_label_coarse: The coarse label attributed to the query by a model trained with the Li and Roth corpus.
    :param ents: The named entities found by the spacy named entity recognizer.
    :param model_coarse: The trained model for the coarse labels of the multieight corpus.
    :return: A list containing a classification according to the Li & Roth taxonomy. If a classification is not found,
    an empty list is returned.
    """

    classification = []
    key_entity = ''
    if len(ents) > 1:
        for ent in ents:
            if ent.label_ == 'PER' and ent.text not in query:
                key_entity = ent.text
                classification = ['HUM']
            elif ent.label_ == 'ORG' and ent.text not in query:
                if query_label_coarse == 'HUM':
                    classification = ['HUM', 'gr']
            elif ent.label_ == 'LOC' and ent.text not in query:
                key_entity = ent.text
                classification = ['LOC']

    if key_entity and len(classification) < 2:
        classification.append(*model_loader('multieight' + classification[0], 'answer').predict([key_entity, ]).tolist())
    elif key_entity and len(classification) < 2:
        classification = model_coarse.predict([key_entity, ]).tolist()
        classification.append(*model_loader('multieight' + classification[0], 'answer').predict([key_entity, ]).tolist())

    return classification


def enty_with_rules(query_label_coarse: str, query_label_fine: str, doc_answer: spacy.tokens.doc.Doc,
                    answer_tokenized_no_stopwords: list, query_tokenized_stopwords: list, answer_tokenized: list) \
        -> list:

    """
    This function uses wordnet to find all hyponyms of the fine category of the query and then it loops through the
    words of the answer to see if any of them is an hyponym of that fine category. If one is found, the classification
    for the answer is also found (the same as the one in the query). This, though, is just for some fine categories.
    Some aren't possible with this method and some are found with other methods. The fine category termeq is found if a
    word of the answer is a synonym of a word of the query. The fine category letter is given to the answer if an
    isolated letter is found on the answer.

    :param query_label_coarse: The coarse label attributed to the query by a model trained with the Li and Roth corpus.
    :param query_label_fine: The coarse label attributed to the query by a model trained with the Li and Roth corpus.
    :param doc_answer: The answer of the agent on the format of spacy.
    :param answer_tokenized_no_stopwords: The answer of the agent tokenized without any stopwords.
    :param query_tokenized_stopwords: The query that the user introduced in the system tokenized and without any
    stopwords.
    :param answer_tokenized: The answer of the agent tokenized.
    :return: A list containing a classification according to the Li & Roth taxonomy. If a classification is not found,
    an empty list is returned.
    """

    classification = []
    if query_label_fine == 'animal':
        hypernym = [wn.synsets('animal', lang='por')[0]]
    elif query_label_fine == 'body':
        hypernym = [wn.synsets('órgão', lang='por')[4]]
    elif query_label_fine == 'color':
        hypernym = [wn.synsets('cor', lang='por')[2]]
    elif query_label_fine == 'currency':
        hypernym = wn.synsets('moeda', lang='por')[1:-2] + [wn.synsets('moeda', lang='por')[-1]]
    elif query_label_fine == 'dismed':
        hypernym = wn.synsets('vírus', lang='por') + wn.synsets('bactéria', lang='por') + wn.synsets('infecção',
                                                                                                     lang='por') + \
                   wn.synsets('doença', lang='por')[:-1] + wn.synsets('remédio', lang='por') + [
                       wn.synsets('comprimido', lang='por')[-1]]
    elif query_label_fine == 'veh':
        hypernym = wn.synsets('veículo', lang='por')
    elif query_label_fine == 'sport':
        hypernym = wn.synsets('esporte', lang='por')
    elif query_label_fine == 'plant':
        hypernym = [wn.synsets('planta', lang='por')[0]]
    elif query_label_fine == 'religion':
        hypernym = wn.synsets('religião', lang='por')[1:]
    elif query_label_fine == 'food':
        hypernym = wn.synsets('comida', lang='por')[:-1]
    elif query_label_fine == 'substance':
        hypernym = wn.synsets('substância', lang='por')[:-2] + [wn.synsets('substância', lang='por')[-1]]
    elif query_label_fine == 'lang':
        hypernym = wn.synsets('linguagem', lang='por')[1:3]
    elif query_label_fine == 'instru':
        hypernym = wn.synsets('instrumento', lang='por')[4]
    elif query_label_fine == 'techmeth':
        hypernym = [wn.synsets('técnica', lang='por')[3]] + wn.synsets('método', lang='por')
    elif query_label_fine == 'event':
        hypernym = wn.synsets('instrumento', lang='por')[0]
    elif query_label_fine == 'product':
        hypernym = wn.synsets('produto', lang='por')[4]
    elif query_label_fine == 'symbol':
        hypernym = [wn.synsets('símbolo', lang='por')[0]] + [wn.synsets('símbolo', lang='por')[2]] + \
                   [wn.synsets('sinal', lang='por')[2]] + [wn.synsets('sinal', lang='por')[-3]]
    elif query_label_fine == 'letter':
        hypernym = wn.synsets('letra', lang='por')[1]
        letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for word in answer_tokenized:
            if len(word) == 1 and word in letters:
                classification = ['ENTY', 'letter']

    elif query_label_fine == 'termeq':
        for word in answer_tokenized_no_stopwords:
            for word2 in query_tokenized_stopwords:
                if look_synonyms(word, word2):
                    classification = ['ENTY', 'termeq']

    if 'hypernym' in locals():
        for word in doc_answer:
            if word.text.lower() not in query_tokenized_stopwords:
                hyponym = wn.synsets(str(word), lang='por')
                if len(classification) == 2:
                    break
                if not hyponym:
                    hyponym = wn.synsets(str(word.lemma_), lang='por')
                for h in hyponym:
                    if look_synset_tree(hypernym, h):
                        classification = [query_label_coarse, query_label_fine]
                        break
    return classification


def get_translation(coarse_label: str, fine_label: str) -> str:

    """
    This function simply maps the tags of the Li & Roth taxonomy to the portuguese language. It receives them in the
    original form and returns the translated fine category.

    :param coarse_label: The coarse label of the Li & Roth's taxonomy.
    :param fine_label: The fine label of the Li & Roth's taxonomy to be translated.
    :return: The fine label translated.
    """

    dict_fine = {'ABBR': ['abb', 'exp'],
                 'ENTY': ['animal', 'body', 'color', 'cremat', 'currency', 'dismed', 'event', 'food', 'instru', 'lang',
                          'letter', 'other', 'plant', 'product', 'religion', 'sport', 'substance', 'symbol', 'techmeth',
                          'termeq', 'veh', 'word'],
                 'DESC': ['def', 'desc', 'manner', 'reason'],
                 'HUM': ['gr', 'ind', 'title', 'desc'],
                 'LOC': ['city', 'country', 'mount', 'other', 'state'],
                 'NUM': ['code', 'count', 'date', 'dist', 'money',
                         'ord', 'other', 'period', 'perc', 'speed', 'temp', 'volsize', 'weight'],

                 }

    dict_pt = {'ABBR': ['abreviação', 'expressão'],
               'ENTY': ['animal', 'corpo', 'cor', 'criatividade', 'moeda', 'doença', 'evento', 'comida', 'instrumento',
                        'linguagem', 'letra', 'outro', 'planta', 'produto', 'religião', 'desporto', 'substância',
                        'símbolo', 'técnica', 'termo', 'veículo', 'palavra'],
               'DESC': ['definição', 'descrição', 'maneira', 'razão'],
               'HUM': ['grupo', 'indivíduo', 'título', 'descrição'],
               'LOC': ['cidade', 'país', 'montanha', 'outro', 'estado'],
               'NUM': ['código', 'contagem', 'data', 'distância', 'dinheiro',
                       'ordem', 'outro', 'período', 'percentagem', 'velocidade', 'temperatura', 'tamanho', 'peso'],

               }

    return dict_pt[coarse_label][dict_fine[coarse_label].index(fine_label)]


def ngrams_strings_builder(string_tokenized: list) -> list:

    """
    This function receives a string tokenized and returns a list containing subsets of this string from subsets of one
    word to a subset with the whole sentence and all in between.

    :param string_tokenized: A list containing a string tokenized.
    :return: A list containing string subsets of size one to the size of the sentence.
    """

    string_ngrams = [ngrams(string_tokenized, i) for i in range(0, len(string_tokenized))]
    parts_of_string = []
    for lst in string_ngrams:
        aux = []
        for tpl in lst:
            parts = ''
            for el in tpl:
                parts += el + ' '
            aux += [parts[:-1]]
        parts_of_string += aux
    parts_of_string.reverse()
    return parts_of_string


def wikipedia_classification(query_label_coarse: str, query_label_fine: str, answer_tokenized: list) -> list:

    """
    This function uses wikipedia api to find if, when searching for the agent's answer or parts of this answer, the word
    or words related to the query's fine category according to the Li & Roth taxonomy, appears in the results. That is,
    if parts of the answer and the query's fine label appear together in a wikipedia article.

    :param query_label_coarse: The coarse label attributed to the query by a model trained with the Li and Roth corpus.
    :param query_label_fine: The coarse label attributed to the query by a model trained with the Li and Roth corpus.
    :param answer_tokenized: The answer of the agent tokenized.
    :return: A list containing a classification according to the Li & Roth taxonomy. If a classification is not found,
    an empty list is returned.
    """
    import time
    start_time = time.time()

    wikipedia.set_lang("pt")
    classification = []
    label_fine_pt = get_translation(query_label_coarse, query_label_fine)

    list_of_labels = ['cidade', 'país', 'montanha', 'estado', 'animal', 'corpo', 'cor', 'moeda',
                      'doença', 'remédio', 'evento', 'comida', 'instrumento', 'linguagem', 'letra',
                      'planta', 'produto', 'religião', 'desporto', 'substância',
                      'símbolo', 'técnica', 'veículo']
    if label_fine_pt not in list_of_labels and label_fine_pt!='criatividade' and label_fine_pt!='grupo' and \
            query_label_coarse != 'LOC' and query_label_fine!='other':
        return classification
    parts_of_answer = ngrams_strings_builder(answer_tokenized)
    list_of_important_words = []
    if label_fine_pt == 'criatividade':
        list_of_important_words = ['musical', 'musicais', 'filme', 'filmes', 'livro', 'livros', 'composição',
                                   'composições', 'música', 'músicas', 'quadro', 'quadros', 'pintura', 'pinturas',
                                   'mural', 'murais', 'teatro', 'teatros', 'peça', 'peças', 'literatura', 'literaturas',
                                   'escultura', 'esculturas', 'coreografia', 'coreografias', 'dança', 'danças',
                                   'ilusionismo', 'jogo', 'jogos', 'fotografia', 'fotografias', 'tira', 'tiras',
                                   'videojogo', 'videojogos', 'romance', 'drama', 'acção', 'ação', 'terror', 'thriller',
                                   'suspense']
        list_of_composed_creativity = ['banda desenhada', 'bandas desenhadas', 'obra literária', 'obras literárias']
    elif label_fine_pt == 'grupo':
        list_of_important_words = ['equipa', 'equipe', 'empresa', 'organização', 'instituição', 'associação',
                                   'sociedade', 'grupo', 'companhia']
    elif query_label_coarse == 'LOC' and query_label_fine=='other':
        list_of_important_words = ['aldeia', 'vila', 'freguesia', 'estádio', 'teatro', 'cinema', 'restaurante', 'centro',
                         'terra', 'casa', 'distrito', 'parque', 'país', 'cidade', 'montanha', 'monte',
                         'palácio', 'castelo', 'rio', 'lagoa', 'cordilheira', 'oceano', 'mar', 'continente']
    else:
        if label_fine_pt in list_of_labels:
            list_of_important_words = [label_fine_pt]
            parts_of_answer = answer_tokenized
    for parts in parts_of_answer:
        if (time.time() - start_time) > 20:
            return []
        if len(parts) <= 300:
            try:
                summary = wikipedia.summary(parts)
                list_of_words = word_tokenize(summary.lower())
                for word in list_of_important_words:
                    if word in list_of_words:
                        classification = [query_label_coarse, query_label_fine]
                if 'list_of_composed_creativity' in locals():
                    for words in list_of_composed_creativity:
                        if words in summary:
                            classification = [query_label_coarse, query_label_fine]
                if classification:
                    return classification
            except wikipedia.exceptions.PageError:
                # if a "PageError" was raised, ignore it and continue to next link
                continue
            except wikipedia.DisambiguationError as e:
                # if there is more than one article to a given word, as it would take a toll on the efficiency to iterate
                # through them all, we just ignore this word.
                continue

    return classification


def answer_classification(query: str, query_label_coarse: str, query_label_fine: str, answer: str) -> tuple:

    """
    This function uses the query's classification labels (obtained with a model trained in the Li and Roth corpus)
    to look for words in the answer that might be related to that classification of the query. To perform this search
    in the answer, the function first tries to look for it in the wikipedia (only for some labels). If it does not
    get to a classification using wikipedia, it then uses modules such as wordnet, NER and regex to get to a
    classification. If it still does not achieve one, it uses a model trained in the multieight corpus which contains
    questions and answers labelled with the Li and Roth taxonomy. In the end, a tuple containing a list containing a
    classification of the answer with the format [answer_label_coarse, answer_label_fine] and a score of how much of a
    match the answer classification is to the query classification.

    :param query: The query inserted by the user.
    :param query_label_coarse: The coarse label attributed to the query by a model trained with the Li and Roth corpus.
    :param query_label_fine: The coarse label attributed to the query by a model trained with the Li and Roth corpus.
    :param answer: The answer of one agent to the query inserted by the user.
    :return: A tuple containing list with a coarse and a fine label classification of the answer given by the agent and
    a score of how much of a match the answer classification is to the query classification.
    """

    model_coarse = model_loader('multieight', 'answer')
    answer_tokenized = word_tokenize(answer.lower())
    nlp = spacy.load("pt_core_news_sm")
    doc_answer = nlp(answer)
    ents = doc_answer.ents
    answer_tokenized_no_lower = word_tokenize(answer)

    query_tokenized = word_tokenize(query.lower())
    stopword = set(stopwords.words('portuguese') + list(punctuation) + stopwords.words('english'))
    stopword2 = set(stopwords.words('portuguese') + stopwords.words('english'))
    answer_tokenized_no_stopwords_query = [word for word in answer_tokenized if word not in stopword and word not in word_tokenize(query.lower())]
    answer_tokenized_no_stopwords = [word for word in answer_tokenized if word not in stopword2]
    query_tokenized_stopwords = [word for word in query_tokenized if word not in stopword]
    classification = []
    answer_list = [word for word in answer_tokenized_no_lower if word not in query_tokenized]
    answer = ''

    for word in answer_list:
        answer += word + ' '

    try:
        urllib2.urlopen('http://91.198.174.192', timeout=1)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            classification = wikipedia_classification(query_label_coarse, query_label_fine, answer_list)
    except urllib2.URLError:
        pass

    if not classification:
        if query_label_coarse == 'ENTY':
            classification = enty_with_rules(query_label_coarse, query_label_fine, doc_answer, answer_tokenized_no_stopwords_query,
                                             query_tokenized_stopwords, answer_tokenized)
        elif query_label_coarse == 'HUM' or query_label_coarse == 'LOC':
            classification = loc_hum_rules(query, query_label_coarse, ents, model_coarse)
        elif query_label_coarse == 'NUM':
            classification = num_rules(query_label_fine, answer, answer_tokenized, doc_answer)
        elif query_label_coarse == 'ABBR':
            classification = abbr_rules(query, query_label_fine, answer_tokenized_no_stopwords, answer_tokenized_no_lower)
        if not classification:
            classification = model_coarse.predict([answer]).tolist()
        if len(classification) == 1:
            classification += model_loader('multieight' + classification[0], 'answer').predict([answer]).tolist()

    score = 0
    if query_label_coarse in classification:
        score += 0.5
    if query_label_fine in classification:
        score += 0.5
    return classification, score

