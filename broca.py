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
    SQLReturn = None
    with connection:
        cursor.execute('SELECT * FROM conceptgraph WHERE noun = "%s" AND association_type = 1;' % noun)
        SQLReturn = cursor.fetchall()
        # add all found associations to a dictionary, paired with their association strength
        if SQLReturn:
            for item in SQLReturn:
                association = item[3]
                strength = item[7]
                partOfSpeech = item[4]
                verbTupe = (association, strength, partOfSpeech)
                foundAssociations.append(verbTupe)
    return foundAssociations

def findrelatednouns(nounList, verbList):
    with connection:
        for noun in nounList:
            cursor.execute('SELECT * FROM conceptgraph WHERE noun = "%s" AND association_type = 0;' % noun)
        SQLReturnNoun = cursor.fetchall()

        for verb in verbList:
            cursor.execute('SELECT * FROM conceptgraph WHERE association = "%s" AND association_type = 1;' % verb)
        SQLReturnVerb = cursor.fetchall()
        # todo: compare the two and merge

def findrelatedadjectives(GeneratedNounList):
    print "I'm empty"
    # note: this nounList is the list of nouns from our OUTPUT sentence

def insertverbs(sentenceTemplate, relatedVerbs):
    verbList = []
    verbPosition = []
    for count in range(0, len(sentenceTemplate)):       # get list of verbs and their indexes
        pos = sentenceTemplate[count]
        if pos in cfg.verbCodes():
            verbList.append(pos)
            verbPosition.append(count)

    if verbList:                                        # if we have any verbs in the sentence model, try to match them to associated verbs
        # todo: if we can't match verb types perfectly, should we fall back to allow all verbs to fill a space before going to printing "?"?
        for count in range(0, len(verbList)):           # goes thru verb POS's
            possibleWords = []
            dieTotal = 0.0
            for verbTupe in relatedVerbs:               # matches related verbs by pos
                if len(verbTupe) > 0 and verbTupe[2] == verbList[count]:      # this will have a problem if there are no related verbs
                    possibleWords.append(verbTupe)
            for verbTupe in possibleWords:              # rolls die weighted by strength of related matching verbs
                dieTotal += verbTupe[1]
            dieRoll = random.uniform(0, dieTotal)
            for verbTupe in possibleWords:
                dieRoll -= verbTupe[1]
                if dieRoll < 0:
                    sentenceTemplate[verbPosition[count]] = verbTupe[0] # adds verb based on die to template
                    # todo: remove verb so that it cannot be used twice
                    break
        for count, pos in enumerate(sentenceTemplate):  # replace leftover verbs with "?"
            if pos in verbCodes:
                sentenceTemplate[count] = "?"
    return sentenceTemplate