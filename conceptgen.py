# Name:             Concept Generator
# Description:      Takes word inputs, links and stores them as an association in the concept graph
# Section:          LEARNING
# Writes/reads:     emma.brn/conceptgraph.db
# Dependencies:     sqlite3
# Dependency of:    emma
import sqlite3 as sql, cfg

connection = sql.connect('emma.brn/conceptgraph.db')        # connect to the concept graph SQLite database
cursor = connection.cursor()                                # get the cursor object

# declare parts of speech umbrellas for findassociations()
nounCodes = cfg.nounCodes()
verbCodes = cfg.verbCodes()
adjectiveCodes = cfg.adjectiveCodes()

# load list of banned words into a dictionary so that we can stop them from being added into associations
with open('emma.brn/bannedwords.txt') as bannedWordsFile:
    bannedWords = []
    for line in bannedWordsFile:                            # pump banned words into a list, word by word
        bannedWord = line
        bannedWords.append(bannedWord.rstrip('\n'))         # remove newline characters as we add banned words to the list

def findassociations(inputAsWords, inputAsPOSTuple):
    ### given a sentence, find important words and create associations between them
    ## get POS sentence from POS Tuple
    inputAsPOS = []
    for count in range(0, len(inputAsPOSTuple)):
        inputPOSTuple = inputAsPOSTuple[count]
        inputAsPOS.append(inputPOSTuple[1])
    
    for count1 in range(0, len(inputAsWords)):   
        ## iterate through each word in the sentence              
        if inputAsPOS[count1] in nounCodes:                 # if the word isn't a noun, we aren't interested in it
            noun = inputAsWords[count1]
            # todo: make these one function somehow
            # look for important words after noun
            for count2 in range(count1 + 1, len(inputAsWords)):
                importantWord = True
                if inputAsPOS[count2] in nounCodes:
                    associationType = 0
                elif inputAsPOS[count2] in verbCodes:
                    associationType = 1
                elif inputAsPOS[count2] in adjectiveCodes:
                    associationType = 2
                else:
                    importantWord = False
                if importantWord:                           # if an important word is found, add an association to the Concept Graph
                    association = inputAsWords[count2]
                    associationPOS = inputAsPOS[count2]
                    proximity = count2 - count1
                    addconcept(noun, associationType, association, associationPOS, proximity)
                
            # look for important words before noun
            for count3 in range(0, count1):
                importantWord = True
                if inputAsPOS[count3] in nounCodes:
                    associationType = 0
                elif inputAsPOS[count3] in verbCodes:
                    associationType = 1
                elif inputAsPOS[count3] in adjectiveCodes:
                    associationType = 2
                else:
                    importantWord = False
                if importantWord:                           # if an important word is found, add an association to the Concept Graph
                    association = inputAsWords[count3]
                    associationPOS = inputAsPOS[count3]
                    proximity = count1 - count3
                    addconcept(noun, associationType, association, associationPOS, proximity)
            
def calculateaverages():
    # Calculates averages of all frequencies and all proximities for strength() to use later.
    # It is self-contained in an attempt to save processing power, as these only need to be calculated once per input instead of once per word
    frequencies = []
    proximities = []
    with connection:
        cursor.execute('SELECT total_frequency, average_proximity FROM conceptgraph')   # Get frequencies for strength calculation
        freqAndProx = cursor.fetchall()

        if freqAndProx:                                                                 # check to see if there are any values in the table. If not, we have a divide by zero error when we calculate score
            freqAndProxLength = len(freqAndProx)
            for item in freqAndProx:
                frequencies.append(item[0])
                proximities.append(item[1])
        else:
            freqAndProxLength = 1                                                       # if freqAndProx is empty, we'll use 1 for each value
            frequencies = [1]                                                           # next time scores are calculated they'll become more accurate
            proximities = [1]

        calculateaverages.avgTotalFrequency = sum(frequencies) / freqAndProxLength
        calculateaverages.avgAvgProximity = sum(proximities) / freqAndProxLength

def calculatestrength(totalFreq, avgProx):
    # we have a backup strength equation in case avgAvgProximity = 1, because that creates a divide by zero
    if calculateaverages.avgAvgProximity != 1:
        strength = ((2 * float(totalFreq))/(calculateaverages.avgTotalFrequency + totalFreq)) * 2 ** (1 - ((avgProx - 1)/(calculateaverages.avgAvgProximity - 1)) ** 2)
    else:
        strength = (2 * float(totalFreq))/(calculateaverages.avgTotalFrequency + totalFreq)
    return strength

def addconcept(noun, associationType, association, associationPOS, proximity):
    # start by making sure the word to associate isn't on our list of banned words
    if noun.lower() not in bannedWords and association.lower() not in bannedWords:
        
        # next, calculate average total frequencies and average average proximities to calculate score
        calculateaverages()

        # and then start handling the words themselves
        with connection:
            cursor.execute('SELECT DISTINCT noun FROM conceptgraph;')   # check to see if Emma has seen this word before
            bundledWordList = cursor.fetchall()

            if bundledWordList:                                         # if the concept graph isn't empty
                wordList = []
                for cutWord in bundledWordList:                         # take each word we know and stick it in a list
                    wordList.append(cutWord[0])
                if noun not in wordList:                                # if our noun isn't in that list, it's new
                    print "Learned new word (%s)!" % noun
                    newWordFile = open('emma.brn/newwords.txt', 'a')    # print new word to newwords.txt to learn more about later
                    print >>newWordFile, noun
                    newWordFile.close()

            cursor.execute('SELECT * FROM conceptgraph WHERE noun = \'%s\' AND association = \'%s\';' % (noun, association))     # check to see if the row that we want to work with is already in the database
            row = cursor.fetchone()

            if row != None:                                                             # if we have already made this association, recalculate its values based on new data
                #print "Re-evaluating existing association between %s and %s" % (noun, association)
                conceptid = row[0]
                
                totalFrequency = row[6]

                avgProximity = row[7]                                                   # get current average proximity
                avgProximity = (avgProximity + proximity) / totalFrequency              # calculate new average proximity

                strength = calculatestrength(totalFrequency, avgProximity)              # calculate new association strength

                # COMMIT
                cursor.execute('UPDATE conceptgraph SET total_frequency = total_frequency + 1, average_proximity = %s, strength = %s WHERE concept_id = %s' % (avgProximity, strength, conceptid))

            else:                                                                       # if the row IS NOT a duplicate
                strength = calculatestrength(1, proximity)                              # calculate association strength and create a new association
                print "Creating new association for %s (%s)" % (noun, association)
                cursor.execute('INSERT INTO conceptgraph (noun, association_type, association, association_pos, total_frequency, average_proximity, strength) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', 1, \'%s\', \'%s\');' % (noun, associationType, association, associationPOS, proximity, strength))