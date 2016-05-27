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
    # given a noun, find associated verbs
    noun = noun[0]
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

# todo: merge insert(whatever) functions into one function
def insertverbs(sentenceTemplate, relatedVerbs):
    verbList = []
    verbPosition = []
    usedWords = []
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
                    print possibleWords
            for verbTupe in possibleWords:              # rolls die weighted by strength of related matching verbs
                dieTotal += verbTupe[1]
            dieRoll = random.uniform(0, dieTotal)
            for count, verbTupe in enumerate(possibleWords):
                dieRoll -= int(verbTupe[1])
                if dieRoll < 0 and verbTupe[0] not in usedWords:
                    sentenceTemplate[verbPosition[count]] = verbTupe[0] # adds verb based on die to template
                    usedWords.append(verbTupe[0])
                    break
                    # todo URGENT: if the var IS in usedWords, use the next var in the list
        for count, pos in enumerate(sentenceTemplate):  # replace leftover verbs with "?"
            if pos in verbCodes:
                sentenceTemplate[count] = "?"
    return sentenceTemplate

print insertverbs(['VB', 'VB', 'VBN', 'VBG'], findrelatedverbs(['bee']))

def findrelatednouns(nounList, verbList):
    with connection:
        # fetch nouns related to our nounList and verbList
        for noun in nounList:
            cursor.execute('SELECT * FROM conceptgraph WHERE noun = "%s" AND association_type = 0;' % noun)
        SQLReturnNoun = cursor.fetchall()

        for verb in verbList:
            cursor.execute('SELECT * FROM conceptgraph WHERE association = "%s" AND association_type = 1;' % verb)
        SQLReturnVerb = cursor.fetchall()

        # get lists of nouns and strengths from our noun return
        nounNounList = []
        nounStrengthList = []
        for row in SQLReturnNoun:
            nounNounList.append(row[3])
            nounStrengthList.append(row[7])

        # get lists of nouns and strengths from our verb return
        verbNounList = []
        verbStrengthList = []
        for row in SQLReturnVerb:
            verbNounList.append(row[1])
            verbStrengthList.append(row[7])

        # compare the two lists of nouns and check for duplicates
        for count, noun in enumerate(nounNounList):
            if noun in verbNounList:
                nounNounList.remove(noun)
                verbStrengthList[count] = ((nounStrengthList.index(noun) + verbStrengthList[count]) / 2)
                nounStrengthList.remove(nounStrengthList[count])

        foundNouns = nounNounList + verbNounList
        foundStrengths = nounStrengthList + verbStrengthList

        foundAssociations = zip(foundNouns, foundStrengths)
        return foundAssociations

def insertnouns(sentenceTemplate, relatedNouns):
    relatedNouns = relatedNouns[0]
    nounList = []
    nounPosition = []
    usedWords = []
    for count in range(0, len(sentenceTemplate)):       # get list of nouns and their indexes
        pos = sentenceTemplate[count]
        if pos in cfg.nounCodes():
            nounList.append(pos)
            nounPosition.append(count)

    if len(nounList) > 0:                                        # if we have any nouns in the sentence model, try to match them to associated nouns
        # todo: if we can't match noun types perfectly, should we fall back to allow all nouns to fill a space before going to printing "?"?
        for count in range(0, len(nounList)):           # goes thru noun POS's
            possibleWords = []
            dieTotal = 0.0
            for nounTupe in relatedNouns:               # matches related nouns by pos
                possibleWords.append(nounTupe)
            for nounTupe in possibleWords:              # rolls die weighted by strength of related matching nouns
                dieTotal += int(nounTupe[1])

            dieRoll = random.uniform(0, dieTotal)
            for nounTupe in possibleWords:
                dieRoll -= nounTupe[1]
                if dieRoll < 0 and nounTupe[0] not in usedWords:
                    sentenceTemplate[nounPosition[count]] = nounTupe[0] # adds noun based on die to template
                    usedWords.append(nounTupe[0])
                    break
        for count, pos in enumerate(sentenceTemplate):  # replace leftover nouns with "?"
            if pos in nounCodes:
                sentenceTemplate[count] = "?"
    return sentenceTemplate

def findrelatedadjectives(noun):
    # given a noun, find associated adjectives
    # note: this nounList is the list of nouns from our OUTPUT sentence
    #       also, this is almost identical to findrelatedverbs(). merge?
    foundAssociations = []
    SQLReturn = None
    with connection:
        cursor.execute('SELECT * FROM conceptgraph WHERE noun = "%s" AND association_type = 2;' % noun)
        SQLReturn = cursor.fetchall()
        # add all found associations to a dictionary, paired with their association strength
        if SQLReturn:
            for item in SQLReturn:
                association = item[3]
                strength = item[7]
                partOfSpeech = item[4]
                adjectiveTupe = (association, strength, partOfSpeech)
                foundAssociations.append(adjectiveTupe)
    return foundAssociations

def insertadjectives(sentenceTemplate, relatedAdjectives):
    adjectiveList = []
    adjectivePosition = []
    for count in range(0, len(sentenceTemplate)):       # get list of adjectives and their indexes
        pos = sentenceTemplate[count]
        if pos in cfg.adjectiveCodes():
            adjectiveList.append(pos)
            adjectivePosition.append(count)

    if adjectiveList:                                   # if we have any adjectives in the sentence model, try to match them to associated adjectives
        # todo: if we can't match adjective types perfectly, should we fall back to allow all adjectives to fill a space before going to printing "?"?
        for count in range(0, len(adjectiveList)):      # goes thru adjective POS's
            possibleWords = []
            dieTotal = 0.0
            for adjectiveTupe in relatedAdjectives:     # matches related adjectives by pos
                if len(adjectiveTupe) > 0 and adjectiveTupe[2] == adjectiveList[count]:      # this will have a problem if there are no related adjectives
                    possibleWords.append(adjectiveTupe)
            for adjectiveTupe in possibleWords:         # rolls die weighted by strength of related matching adjectives
                dieTotal += adjectiveTupe[1]
            dieRoll = random.uniform(0, dieTotal)
            for adjectiveTupe in possibleWords:
                dieRoll -= adjectiveTupe[1]
                if dieRoll < 0:
                    sentenceTemplate[adjectivePosition[count]] = adjectiveTupe[0] # adds adjective based on die to template
                    # todo: remove adjective so that it cannot be used twice
                    break
        for count, pos in enumerate(sentenceTemplate):  # replace leftover adjectives with "?"
            if pos in adjectiveCodes:
                sentenceTemplate[count] = "?"
    return sentenceTemplate

# print findrelatednouns(['car'], ['grow']) # should find "tree" and "driver" in association network
#print findrelatedverbs(['cats'])
#dprint insertnouns(['NN', 'NN'], findrelatednouns(['car'], ['grow']))
