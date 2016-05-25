# Name:             Broca's Area
# Description:      Broca's Area ... is a region in the frontal lobe of the dominant hemisphere ... with functions linked to speech production.
# Section:          REPLY
# Writes/reads:     emma.brn/conceptgraph.db
# Dependencies:     sqlite3, cfg
# Dependency of:    emma
import sqlite3 as sql, cfg

connection = sql.connect('emma.brn/conceptgraph.db')        # connect to the concept graph SQLite database
cursor = connection.cursor()                                # get the cursor object

nounCodes = cfg.nounCodes()
verbCodes = cfg.verbCodes()
adjectiveCodes = cfg.adjectiveCodes()

def findrelatedverbs(nounList):
    with connection:
        for count in range(0, len(nounList)):
            cursor.execute('SELECT * FROM conceptgraph WHERE noun = "%s" AND association_type = 1;' % nounList[count])
        SQLReturn = cursor.fetchall()

        foundWords = {}
        for count in range(0, len(SQLReturn)):  # add all found associations to a dictionary, paired with their association strength
            rowData = SQLReturn[count]
            strength = rowData[7]
            association = rowData[3]
            partOfSpeech = rowData[4]
            foundWords[association] = strength
    return foundWords

def findrelatednouns(nounList, verbList):
    with connection:
        cursor.execute('SELECT * FROM conceptgraph WHERE')

def insertverbs(sentenceTemplate, convonouns, relatedVerbs):
    # Get list of verbs and their indexs
    verbList = []
    verbPosition = []
    for count in range(0, len(sentenceTemplate)):
        pos = sentenceTemplate[count]
        if pos in cfg.verbCodes():
            verbList.append(pos)
            verbPosition.append(count)

    # todo: make this work past just demo levelsf
    for count in verbList[]

    print sentenceTemplate
insertverbs(['VBP', 'JJ', 'NN', '.'], ['god', 'ponies'], [('take', 2.0, 'VBP'), ('taken', 1.3, 'VB')])
insertverbs(['VBP', 'VB', 'NN', '.'], ['god', 'ponies'], [('take', 2.0, 'VBP'), ('taken', 1.3, 'VB')])
