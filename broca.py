# Name:             Broca's Area
# Description:      Broca's Area ... is a region in the frontal lobe of the dominant hemisphere ... with functions linked to speech production.
# Section:          REPLY
# Writes/reads:     emma.brn/conceptgraph.db
# Dependencies:     sqlite3, cfg, random, nltk
# Dependency of:    emma
import sqlite3 as sql, cfg, random, nltk

connection = sql.connect('emma.brn/conceptgraph.db')        # connect to the concept graph SQLite database
cursor = connection.cursor()                                # get the cursor object

nounCodes = cfg.nounCodes()
verbCodes = cfg.verbCodes()
adjectiveCodes = cfg.adjectiveCodes()

def findrelatedverbs(noun):
    # given a noun, find verbs that are associated with it
    foundWords = []
    foundAssociations = []
    with connection:
        cursor.execute('SELECT * FROM conceptgraph WHERE noun = "%s" AND association_type = 1;' % noun)
        SQLReturn = cursor.fetchall()
        # add all found associations to a dictionary, paired with their association strength
        rowData = SQLReturn[0]
        print rowData
        association = rowData[3]
        strength = rowData[7]
        partOfSpeech = rowData[4]
        verbtupe = (association, strength, partOfSpeech)
        foundAssociations.append(verbtupe)

    return foundAssociations

def findrelatednouns(nounList, verbList):
    with connection:
        for count in range(0, len(nounList)):
            cursor.execute('SELECT * FROM conceptgraph WHERE noun = "%s" AND association_type = 0;' % nounList[count])
        SQLReturnNoun = cursor.fetchall()

        for count in range(0, len(verbList)):
            cursor.execute('SELECT * FROM conceptgraph WHERE association = "%s" AND association_type = 1;' % verbList[count])
        SQLReturnVerb = cursor.fetchall()
        # todo: compare the two and merge

def findrelatedadjectives(GeneratedNounList):
    print "I'm empty"
    # note: this nounList is the list of nouns from our OUTPUT sentence

def insertverbs(sentenceTemplate, convoNouns, relatedVerbs):
    verbList = []
    verbPosition = []
    for count in range(0, len(sentenceTemplate)):       # Get list of verbs and their indexes
        pos = sentenceTemplate[count]
        if pos in cfg.verbCodes():
            verbList.append(pos)
            verbPosition.append(count)

    for count in range(0, len(verbList)):               # goes thru verb POS's
        possibleWords = []
        dieTotal = 0.0
        for verbtupe in relatedVerbs:                   # matches related verbs by POS
            if verbtupe[2] == verbList[count]:
                possibleWords.append(verbtupe)
        for verbtupe in possibleWords:                  # rolls die weighted by strength of related matching verbs
            dieTotal += verbtupe[1]
        dieRoll = random.uniform(0, dieTotal)
        for verbtupe in possibleWords:
            dieRoll -= verbtupe[1]
            if dieRoll < 0:
                sentenceTemplate[verbPosition[count]] = verbtupe[0] # adds verb based on die to template
                break

    print sentenceTemplate
# insertverbs(['VBP', 'JJ', 'NN', '.'], ['god', 'ponies'], [('take', 2.0, 'VBP'), ('taken', 1.3, 'VB'), ('make', 1.3, 'VBP')])
# insertverbs(['VBP', 'VB', 'NN', '.'], ['god', 'ponies'], [('take', 2.0, 'VBP'), ('taken', 1.3, 'VB'), ('make', 1.3, 'VBP')])
# insertverbs(['VBP', 'VBP', 'NN', '.'], ['god', 'ponies'], [('take', 2.0, 'VBP'), ('taken', 1.3, 'VB'), ('make', 1.3, 'VBP')])
# insertverbs(['VBP', 'NN', 'VB', '.'], ['god', 'ponies'], [('take', 2.0, 'VBP'), ('taken', 1.3, 'VB'), ('make', 1.3, 'VBP')])
# insertverbs(['VBN', 'NN', 'VB', '.'], ['god', 'ponies'], [('take', 2.0, 'VBP'), ('taken', 1.3, 'VB'), ('make', 1.3, 'VBP')]) #note this case has a verb cod in the template but no verb matching that code is related in the brain
#print findrelatedverbs(['fox', 'moon'])
# insertverbs(['VBZ'], ['fox'], findrelatedverbs(['fox']))
