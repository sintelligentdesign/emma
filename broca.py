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

def findrelatedwords(noun, associationType):
    with connection:
        SQLRequest = 'SELECT * FROM conceptgraph WHERE noun = "%s" AND association_type = ' % noun
        if associationType == 0:    # noun-noun association
            SQLRequest += "0;"
        elif associationType == 1:  # noun-verb association
            SQLRequest += "1;"
        elif associationType == 2:  # noun-adjective association
            SQLRequest += "2;"

        cursor.execute(SQLRequest)
        SQLReturn = cursor.fetchall()

        foundWords = {}
        for count in range(0, len(SQLReturn)):  # add all found associations to a dictionary, paired with their association strength
            rowData = SQLReturn[count]
            strength = rowData[7]
            association = rowData[3]
            partOfSpeech = rowData[4]
            foundWords[association] = strength
    return foundWords

def insertverbs(sentenceTemplate, convonouns, relatedVerbs, verbDictionary):
    # Unzip verbDictionary
    verbList = []
    verbPosition = []
#    for key in verbDictionary:
#        verbList.append(key)
#        verbPosition.append(verbDictionary[key])

    for count in range(0, len(sentenceTemplate)):
        pos = sentenceTemplate[count]
        if pos in cfg.verbCodes():
            verbList.append(pos)
            verbPosition.append(count)
            print pos
            print verbList
            print verbPosition

    # todo: make this work past just demo levels
    for count1 in range(0, len(verbList)):
        for count2 in range(0, len(sentenceTemplate)):
            if verbPosition[count1] == count2:
                verbToInsert = relatedVerbs[0]
                verbToInsert = verbToInsert[0]
                sentenceTemplate[count2] = verbToInsert
    print sentenceTemplate
insertverbs(['VBP', 'JJ', 'NN', '.'], ['god', 'ponies'], [('jump', 2.0), ('gnaw', 1.3)], {'VBP': 0})
insertverbs(['VBP', 'VB', 'NN', '.'], ['god', 'ponies'], [('jump', 2.0), ('gnaw', 1.3)], {'VBP': 0})
