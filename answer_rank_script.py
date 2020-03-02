import operator, classification, personal_answers, impersonal_answers, plug_and_play, query_agent_label_match,\
    query_answer_label_match, chatuga, random
from agents import *
import multiprocessing
import numpy as np
from multiprocessing import Process

curr_dir = os.path.dirname(os.path.abspath(__file__))

def answer_rank_eval_script(agents_dict: dict, corpora_dict: dict, system_dict: dict):
    """
        - 5 coisas do género: bom dia, boa tarde, etc.
        - 10 perguntas do edgar;
        - 10 perguntas do AMA;
        - 25 questões impessoais;
        - 25 questões pessoais; (dos respectivos corpus de teste)
        - 5 yes/no
        - 5 or questions
        - 5 list questions
        - 10 queries que são non-questions
    """
    edgar_corpus = open('/home/mariana/PycharmProjects/ChaTuga v2/novo corpora/query/Treino/edgar_corpus_so_questoes.txt', mode='r', encoding='utf-8-sig')
    ama_corpus = open('/home/mariana/PycharmProjects/ChaTuga v2/novo corpora/query/AMA_corpus_query.txt', mode='r', encoding='utf-8-sig')
    im_personal_corpus = open('/home/mariana/PycharmProjects/ChaTuga v2/novo corpora/query/Treino/personalImpersonal.txt', mode='r', encoding='utf-8-sig')
    list_questions_corpus = open('/home/mariana/Talkit/resources/corpora/listQuestions.txt', mode='r', encoding='utf-8-sig')
    or_questions_corpus = open('/home/mariana/Talkit/resources/corpora/or_questions.txt', mode='r', encoding='utf-8-sig')
    yn_questions_corpus = open('/home/mariana/PycharmProjects/ChaTuga v2/novo corpora/query/Treino/ynQuestion.txt', mode='r', encoding='utf-8-sig')
    non_questions_corpus = open('/home/mariana/PycharmProjects/ChaTuga v2/novo corpora/query/Treino/questionNonQuestion.txt', mode='r', encoding='utf-8-sig')
    social_acks_corpus = open('/home/mariana/Talkit/resources/corpora/smallTalk.txt', mode='r', encoding='utf-8-sig')

    edgar_corpus_lines = [bytes(s, 'utf-8').decode('utf-8','ignore').rstrip().replace('/', ' ou ') for s in list(edgar_corpus)]
    ama_corpus_lines = [bytes(s, 'utf-8').decode('utf-8','ignore').rstrip().replace('/', ' ou ') for s in list(ama_corpus)]
    im_personal_corpus_lines = [bytes(s, 'utf-8').decode('utf-8','ignore').rstrip().replace('/', ' ou ') for s in list(im_personal_corpus)]
    list_questions_list = [bytes(s, 'utf-8').decode('utf-8','ignore').rstrip().replace('/', ' ou ') for s in list(list_questions_corpus)]
    or_questions_list = [bytes(s, 'utf-8').decode('utf-8','ignore').rstrip().replace('/', ' ou ') for s in list(or_questions_corpus)]
    yn_questions_list = [bytes(s, 'utf-8').decode('utf-8','ignore').rstrip().replace('/', ' ou ') for s in list(yn_questions_corpus)]
    non_questions_list = [bytes(s, 'utf-8').decode('utf-8','ignore').rstrip().replace('/', ' ou ') for s in list(non_questions_corpus)]
    social_acks_list = [bytes(s, 'utf-8').decode('utf-8','ignore').rstrip().replace('/', ' ou ') for s in list(social_acks_corpus)]
    #print(edgar_corpus_lines)
    #print(ama_corpus_lines)
    #print(im_personal_corpus_lines)
    #print(list_questions_list)
    #print(or_questions_list)
    #print(yn_questions_list)
    #print(non_questions_list)
    #print(social_acks_list)

    edgar = []
    ama = []
    personal = []
    impersonal = []
    list_questions = []
    or_questions = []
    yn_questions = []
    non_questions = []
    social_acks = []

    print('starting the collect...')

    while len(edgar) < 10:
        query = random.choice(edgar_corpus_lines).split('\t')[1]
        if query not in edgar:
            edgar.append(query)
    while len(ama) < 10:
        query = random.choice(ama_corpus_lines).split('\t')[1]
        if query not in ama:
            ama.append(query)
    while len(personal) < 25 or len(impersonal) < 25:
        query = random.choice(im_personal_corpus_lines)
        query_tag = query.split('\t')[0]
        query_text = query.split('\t')[1]
        if query_tag == 'PERSONAL' and query_text not in personal and len(personal) < 25:
            personal.append(query_text)
        elif query_tag == 'IMPERSONAL' and query_text not in impersonal and len(impersonal) < 25:
            impersonal.append(query_text)
    while len(list_questions) < 5:
        query = random.choice(list_questions_list).split('\t')[1]
        if query not in list_questions and query not in personal and query not in impersonal:
            list_questions.append(query)
    while len(or_questions) < 5:
        query = random.choice(or_questions_list).split('\t')[1]
        if query not in or_questions and query not in personal and query not in impersonal:
            or_questions.append(query)
    while len(yn_questions) < 5:
        query = random.choice(yn_questions_list)
        query_label = query.split('\t')[0]
        query_text = query.split('\t')[1]
        if query_text not in yn_questions and query_label == 'YN_QUESTION' and query not in personal and query not in impersonal:
            yn_questions.append(query_text)
    while len(social_acks) < 5:
        query = random.choice(social_acks_list)
        if query not in social_acks:
            social_acks.append(query)
    while len(non_questions) < 10:
        query = random.choice(non_questions_list).split('\t')
        query_label = query[0]
        query_text = query[1]
        if query_label == 'NON_QUESTION' and query_text not in non_questions:
            non_questions.append(query_text)
    print(len(ama))
    print(len(edgar))
    print(len(personal))
    print(len(impersonal))
    print(len(non_questions))
    print(len(social_acks))
    print(len(yn_questions))
    print(len(or_questions))
    print(len(list_questions))
    print('ended the collect...')

    answer_rank_eval_lines = social_acks + edgar + ama + personal + impersonal + yn_questions + or_questions + non_questions + list_questions
    #print(answer_rank_eval_lines)
    random.shuffle(answer_rank_eval_lines)
    #print(answer_rank_eval_lines)
    print(len(answer_rank_eval_lines))

    dict_of_files = {'eval_ar_edgar.txt': edgar, 'eval_ar_ama.txt': ama, 'eval_ar_yn.txt': yn_questions, 'eval_ar_non_questions.txt': non_questions,
                    'eval_ar_or.txt': or_questions, 'eval_ar_list.txt': list_questions, 'eval_ar_personal.txt': personal, 'eval_ar_impersonal.txt': impersonal,
                    'eval_social_acks.txt': social_acks, 'complete_list_ar.txt': answer_rank_eval_lines}

    print('writing the files...')
    for file in dict_of_files:
        corpus = dict_of_files[file]
        with open(file, mode='w', encoding='utf-8-sig') as f:
            for item in corpus:
                f.write("%s\n" % item)
    print('files written...')

    to_file = ''
    for query in answer_rank_eval_lines:
        print(query)
        print('query ' + str(answer_rank_eval_lines.index(query)) + ' of 100')
        answer_dict, boss_results, predictions_query = chatuga_2(query, agents_dict, corpora_dict, system_dict)
        score_dict = boss_results[0]
        answer_tags = boss_results[1]

        score_dict_aux = sorted(score_dict.items(), key=operator.itemgetter(1))
        score_dict_aux.reverse()
        score_dict = dict(score_dict_aux)
        new_list = sorted(answer_dict.items(), key=lambda agent: score_dict[agent[0]])
        new_list.reverse()
        answer_list = dict(new_list)

        to_file += query + '\t' + str(predictions_query) + '\n'
        ranks = {agent: 0 for agent in score_dict}
        scores = list(score_dict.items())
        for i in range(0, len(scores)):
            if i > 0:
                if scores[i][1] < scores[i-1][1]:
                    ranks[scores[i][0]] = i+1
                elif scores[i][1] == scores[i-1][1]:
                    ranks[scores[i][0]] = ranks[scores[i-1][0]]
                #else:
                #    ranks[scores[i][0]] = i+1
            else:
                ranks[scores[i][0]] = i+1
        for el in ranks:
            to_file += str(ranks[el]) + '\t' + el + '\t' + answer_dict[el] + '\t' + str(score_dict[el]) 
            if answer_dict[el] in answer_tags:
                to_file += '\t' + str(answer_tags[answer_dict[el]]) + '\n'
            else:
                to_file += '\t' + str([]) + '\n'

    print('finished collecting answers, now writing file...')

    answer_file = open('answers_ar.txt', mode='w', encoding='utf-8-sig')
    answer_file.write(to_file)

    print('closing files...')
    edgar_corpus.close()
    ama_corpus.close()
    im_personal_corpus.close()
    list_questions_corpus.close()
    or_questions_corpus.close()
    yn_questions_corpus.close()
    non_questions_corpus.close()
    social_acks_corpus.close()
    answer_file.close()





def chatuga_2(query ,agents_dict: dict, corpora_dict: dict, system_dict: dict):

    """
    This is the main function of the whole project. It receives three dictionaries containing all the information of the
    plug and play config files and it uses that information to reply a user's query with all the agent's answers and
    their scores and orderings.

    :param agents_dict: A dictionary containing all of the agents' informations contained in the agents config xml file
    :param corpora_dict: A dictionary containing all of the corpora information contained in the corpora config xml file
    :param system_dict: A dictionary containing all of the system information contained in the system config xml file
    :return: Not applicable.
    """

    #while True:
        #query = input('Diga algo: ')
    #if query == 'exit':
    #    break

    score_dict = {}

    # Get classification's predictions for the user query

    predictions_query = classification.predict(corpora_dict['query'], query, 'query')

    # Get agent's answers and respective scores

    answer_dict = chatuga.multiprocessing_agents(chatuga.get_agent_answer, agents_dict, query)
    boss_results = chatuga.boss(agents_dict, system_dict, corpora_dict, query, predictions_query, answer_dict)
    score_dict = boss_results[0]
    answer_tags = boss_results[1]

    # Order scores and answers dictionary by scores

    score_dict_aux = sorted(score_dict.items(), key=operator.itemgetter(1))
    score_dict_aux.reverse()
    score_dict = dict(score_dict_aux)
    new_list = sorted(answer_dict.items(), key=lambda agent: score_dict[agent[0]])
    new_list.reverse()
    answer_list = dict(new_list)

    # Calculation of how many hyphens will be needed in the print in order to have the same
    # length as the biggest answer.

    biggest_str_length = 0
    for agent in answer_list:
        if answer_list[agent] in answer_tags:
            if max(len(answer_list[agent]) + len(agent) + 2, len(answer_list[agent]) +
                                         len(' '.join(answer_tags[answer_list[agent]])) + 4) > biggest_str_length:
                biggest_str_length = max(len(answer_list[agent]) + len(agent) + 2, len(answer_list[agent]) +
                                         len(' '.join(answer_tags[answer_list[agent]])) + 4)

        else:
            if max(len(answer_list[agent]) + len(agent) + 2, len(answer_list[agent])
                                     + len('Não foram encontradas etiquetas') + 4) > biggest_str_length:
                biggest_str_length = max(len(answer_list[agent]) + len(agent) + 2, len(answer_list[agent])
                                     + len('Não foram encontradas etiquetas') + 4)

    # Calculation of the agent with the biggest score

    # Find item with Max Value in Dictionary
    itemMaxValue = max(score_dict.items(), key=lambda x: x[1])

    highest_candidates = list()
    # Iterate over all the items in dictionary to find keys with max value
    for key, value in score_dict.items():
        if value == itemMaxValue[1]:
            highest_candidates.append(key)

    # Build a string containing all the information to be shown to the user (scores, agents, labels, answers, etc.)

    to_print = ''
    tags_str = 'Etiquetas da classificação da query:'
    tags_answers = 'Etiquetas da classificação das respostas:'
    scores = 'Scores por agente:'
    candidate = 'Candidato com a melhor classificação:'
    answers = 'Respostas ordenadas por score:'
    to_print += '\n' + (biggest_str_length - len(tags_str)) // 2 * '-' + tags_str + \
                (biggest_str_length - len(tags_str)) // 2 * '-' + '\n'
    to_print += '\n' + str(' '.join(predictions_query)) + '\n'
    to_print += '\n' + (biggest_str_length - len(scores)) // 2 * '-' + scores + \
                (biggest_str_length - len(scores)) // 2 * '-' + '\n'
    for agent in score_dict:
        to_print += '\n' + agent + ': ' + str(score_dict[agent]) + '\n'
    to_print += '\n' + (biggest_str_length - len(candidate))//2 * '-' + candidate + \
                (biggest_str_length - len(candidate))//2 * '-' + '\n'
    if len(highest_candidates) == 1:
        to_print += '\nO candidato com a melhor pontuação foi: ' + highest_candidates[0] + '.\n'
    else:
        to_print += '\nOs candidato com as melhores pontuações (empatados) foram: '
        for el in highest_candidates:
            to_print += el + ' | '
        to_print = to_print[:-3]
        to_print += '.\n'
    to_print += '\n' + (biggest_str_length - len(answers))//2 * '-' + answers + \
                (biggest_str_length - len(answers))//2 * '-' + '\n'
    for agent in answer_list:
        to_print += '\n' + agent + ': ' + answer_list[agent] + '\n'
    to_print += '\n' + (biggest_str_length - len(tags_answers)) // 2 * '-' + tags_answers + \
                (biggest_str_length - len(tags_answers)) // 2 * '-' + '\n'
    for agent in answer_list:
        if answer_list[agent] in answer_tags:
            tags = ' '.join(answer_tags[answer_list[agent]])
        else:
            tags = 'Não foram encontradas etiquetas'
        to_print += '\n' + answer_list[agent] + ' : ' + tags + '.\n'
    to_print += '\n' + biggest_str_length * '-' + '\n'
    #print(to_print)

    # Re-change to the chatuga file directory.

    os.chdir(curr_dir)

    return answer_dict, boss_results, predictions_query

if __name__ == "__main__":
    agents_dicti = plug_and_play.agents_xml_reader(curr_dir + '/agents_config.xml')
    corpora_dicti = plug_and_play.corpora_xml_reader(curr_dir + '/corpora_config.xml')
    system_dicti = plug_and_play.system_xml_reader(curr_dir + '/system_config.xml')
# print(corpora_dicti)
    classification.train(corpora_dicti, 'query')

#    #aux_dict = {'QNQ': corpora_dicti['query']['QNQ']}
# aux_dict.update(corpora_dicti['answer'])
    classification.train(corpora_dicti, 'answer')
    #chatuga(agents_dicti, corpora_dicti, system_dicti)
    answer_rank_eval_script(agents_dicti, corpora_dicti, system_dicti)