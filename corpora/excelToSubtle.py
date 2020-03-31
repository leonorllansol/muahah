'''SubId - 1000
DialogId - 1
Diff - 1
I -  Qual o prazo para pagamento?
R - O prazo para pagamento é de 48 horas após efetuar o pedido. Se o pagamento for efetuado fora do prazo o pedido é cancelado.
'''
import pandas as pd

excel_file = 'bot-FAQ.xlsx'
xlsx = pd.ExcelFile(excel_file)
sheets = []
for sheet in xlsx.sheet_names:
    sheets.append(xlsx.parse(sheet))
    df = pd.concat(sheets,ignore_index=True)
pd.set_option("display.max_rows", None, "display.max_columns", None)

answer_df = df[['TÓPICO','RESPOSTA']]
query_df = df[['TÓPICO','PERGUNTA']]
source_df = df[['PERGUNTA', 'FONTE']]


#if not isinstance(pf, float):

new_file = open('covid.txt', 'w+')
new_file_labels = open('covidLabels.txt', 'w+')
new_file_labels_lst = []
# query and its paraphrases have the same id
query_id = 1
for index, row in df.iterrows():
    paraphrases = [row['PERGUNTA']]

    if not isinstance(row['PARÁFRASES'], float):
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
            source_df = source_df.append(pd.DataFrame({'PERGUNTA':[q],'FONTE':row['FONTE']}),ignore_index=True)

    query_id += 1

    if not row['TÓPICO'] in new_file_labels_lst:
        new_file_labels_lst.append(row['TÓPICO'])
        new_file_labels.write(row['TÓPICO'] + "\n")

new_file.close()
new_file_labels.close()

query_df.columns=['label','query']
answer_df.columns=['label','answer']
source_df.columns=['query','source']
query_df.to_csv("query/covid_query.csv", sep='*', index=False)
answer_df.to_csv("answer/covid_answer.csv", sep='*', index=False)
source_df.to_csv("covid_source.csv", sep='*', index=False)
