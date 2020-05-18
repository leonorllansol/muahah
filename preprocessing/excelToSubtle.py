'''SubId - 1000
DialogId - 1
Diff - 1
I -  Qual o prazo para pagamento?
R - O prazo para pagamento é de 48 horas após efetuar o pedido. Se o pagamento for efetuado fora do prazo o pedido é cancelado.
'''
import pandas as pd

def createQueryAnswerFromExcel(filePath, strToBuildPath, corpusPath, labelsPath):
    #excel_file = 'bot-FAQ.xlsx'

    # try reading excel
    try:
        xlsx = pd.ExcelFile(filePath)
        sheets = []
        # concat multiple excel sheets
        for sheet in xlsx.sheet_names:
            sheets.append(xlsx.parse(sheet))
            df = pd.concat(sheets,ignore_index=True)

    # try reading csv
    except:
        df = pd.read_csv(filePath)

    pd.set_option("display.max_rows", None, "display.max_columns", None)

    answer_df = df[['TÓPICO','RESPOSTA']]
    query_df = df[['TÓPICO','PERGUNTA']]

    if 'FONTE' in df.columns:
        source_df = df[['PERGUNTA', 'FONTE']]

    new_file = open(corpusPath, 'w+')
    new_file_labels = open(labelsPath, 'w+')
    new_file_labels_lst = []
    # query and its paraphrases have the same id
    query_id = 1
    for index, row in df.iterrows():
        paraphrases = [row['PERGUNTA']]

        if 'PARÁFRASES' in df.columns and not isinstance(row['PARÁFRASES'], float):
            paraphrases += row['PARÁFRASES'].split("***")
        for q in paraphrases:
            new_file.write("SubId - 1000\n")
            new_file.write("DialogId - "+ str(query_id) +"\n")
            new_file.write("Diff - 1\n")
            new_file.write("I - " + q + "\n")
            new_file.write("R - " + row['RESPOSTA'] + "\n")
            new_file.write("\n")

            if not q in list(query_df['PERGUNTA']):
                query_df = query_df.append(pd.DataFrame({'TÓPICO': [row['TÓPICO']], 'PERGUNTA': [q]}), ignore_index = True)
                if 'FONTE' in df.columns:
                    source_df = source_df.append(pd.DataFrame({'PERGUNTA':[q],'FONTE':row['FONTE']}),ignore_index=True)

        query_id += 1

        if not row['TÓPICO'] in new_file_labels_lst:
            new_file_labels_lst.append(row['TÓPICO'])
            new_file_labels.write(row['TÓPICO'] + "\n")

    new_file.close()
    new_file_labels.close()

    queryPath = 'corpora/query/' + strToBuildPath + '_query.csv'

    query_df.columns=['label','query']
    query_df.to_csv(queryPath, sep='*', index=False)

    answerPath = 'corpora/answer/' + strToBuildPath + '_answer.csv'
    answer_df.columns=['label','answer']
    answer_df.to_csv(answerPath, sep='*', index=False)

    if 'FONTE' in df.columns:
        sourcePath = 'corpora/' + strToBuildPath + '_source.csv'
        source_df.columns=['query','source']
        source_df.to_csv(sourcePath, sep='*', index=False)
