import xml.etree.ElementTree as ET

"""
GET COVID LABELS FROM FILE AND INSERT THEM INTO AGENTS CONFIG XML
"""
tree = ET.parse('config/agents_config.xml')
root = tree.getroot()

# function to pretty print
def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

# adding an element to the root node
attrib = {'name':'AntiCovidAgent'}
externalAgent = root.makeelement('externalAgent', attrib)
root.append(externalAgent)

labels = externalAgent.makeelement('labels', {})
externalAgent.append(labels)

covid_labels = open("corpora/covidLabels.txt").readlines()
for i in range(len(covid_labels)):
    covid_labels[i] = covid_labels[i].strip('\n')
    attrib = {'score':'1.0'}
    label = labels.makeelement('label', attrib)
    label.text = covid_labels[i]
    labels.append(label)

indent(root)

tree.write('config/agents_config.xml',xml_declaration=True, encoding="UTF-8", method = "xml")
