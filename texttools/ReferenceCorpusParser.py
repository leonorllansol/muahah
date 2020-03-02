from dialog.ReferenceTA import ReferenceTA
import re

class ReferenceCorpusParser:

    def __init__(self, corpusDialoguesPath, corpusLinesPath, corpusSize):
        self.corpusDialoguesPath = corpusDialoguesPath
        self.corpusLinesPath = corpusLinesPath


    def parse(self):

        references = []
        linesMap, linesIndex = self.mapMovieLines()
        dialogues = open(self.corpusDialoguesPath, 'r', encoding='iso-8859-1')
        id = 0

        for line in dialogues.readlines():

            if(line == ""):
                break

            dialog_items = line.split("+++$+++")
            #dialog_lines = dialog_items[3].split("(\',|[\'|\'])")
            dialog_lines = re.split(" \['|', '|'\]",dialog_items[3])

            interaction = self.getInteractionById(dialog_lines[1], linesMap, linesIndex)

            interaction_lines = interaction.split("\n")
            t_items = interaction_lines[0].split("+++$+++")
            a_items = interaction_lines[1].split("+++$+++")
            
            t = t_items[4]
            a = a_items[4]

            rta = ReferenceTA(id, t, a)

            id += 1

            references.append(rta)

        return references


    def mapMovieLines(self):
        linesMap = {}
        linesIndex = {}
        lines = open(self.corpusLinesPath, 'r', encoding='iso-8859-1')
        num = 0

        for l in lines.readlines():
            id = l.split()[0]
            linesMap[id] = (l, num)
            linesIndex[num] = l
            num += 1

        return linesMap, linesIndex



    def getInteractionById(self, id, linesMap, linesIndex):
        line = linesMap[id][0]
        prev_line = linesIndex[linesMap[id][1] - 1]

        return line + prev_line
