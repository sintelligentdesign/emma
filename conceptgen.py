# Concept generator
import sqlite3 as sql

connection = sql.connect('emma.brn/conceptgraph.db')                # connect to the concept graph SQLite database
cursor = connection.cursor()                                # get the cursor object

avgTotalFrequency = 0
avgAvgProximity = 0

def calculateaverages():
    # Calculates averages of all frequencies and all proximities for strength() to use later.
    # It is self-contained in an attempt to save processing power, as these only need to be calculated once per input instead of once per word
    frequencies = []
    proximities = []

    cursor.execute('SELECT total_frequency, average_proximity FROM conceptgraph')   # Get frequencies for strength calculation
    freqAndProx = cursor.fetchall()

    freqAndProxLength = len(freqAndProx)                                            # Index this to save some cycles later
    for count in range(0, freqAndProxLength):
        freqProxStaging = freqAndProx[count]                                        # todo: is there a way we can make this smaller?
        frequencies.append(freqProxStaging[0])
        proximities.append(freqProxStaging[1])
<<<<<<< Updated upstream
                                            
        avgTotalFrequency = sum(frequencies) / freqAndProxLength
        avgAvgProximity = sum(proximities) / freqAndProxLength
=======

        global avgTotalFrequency = sum(frequencies) / freqAndProxLength
        global avgAvgProximity = sum(proximities) / freqAndProxLength
>>>>>>> Stashed changes

def calculatestrength(totalFreq, avgProx):
   strength = ((2 * totalFreq)/(avgTotalFrequency + totalFreq)) * 2 ** (1 - ((avgProx - 1)/(avgAvgProximity - 1)) ** 2)
   return strength

def addconcept(noun, associationType, association, proximity):
    # Start by calculating average total frequencies and average average proximities to calculate score
    calculateaverages()

    # And then start handling the words themselves
    with connection:
        cursor.execute('SELECT DISTINCT noun FROM conceptgraph;')   # check to see if Emma has seen this word before
        fullWordList = cursor.fetchall()
        if fullWordList:
            for count in range(0, len(fullWordList)):
                oldWords = fullWordList[count]
                print oldWords
                if noun in oldWords[0]:
                    print "Learned new word (%s)!" % noun   # todo: this doesn't work and triggers on like every word
                    # todo: search tumblr for new word

        cursor.execute('SELECT * FROM conceptgraph WHERE noun = \'%s\' AND association = \'%s\';' % (noun, association))     # check to see if the row that we want to work with is already in the database
        row = cursor.fetchone()

        if row != None:                                                             # if the row is a duplicate, calculate its new values and add them
            print "Re-evaluating existing association between %s and %s" % (noun, association)

            # GET CONCEPT ID
            conceptid = row[0]

            # TOTAL FREQUENCY
            totalFrequency = row[5]                                                 # get current total frequency
            totalFrequency += totalFrequency                                        # add 1 for new total frequency
                                                                                    # todo: this can be full SQL

            # AVERAGE PROXIMITY
            avgProximity = row[6]                                                   # get current average proximity
            avgProximity = (avgProximity + proximity) / totalFrequency              # calculate new average proximity

            # STRENGTH
            strength = calculatestrength(totalFrequency, avgProximity)              # calculate new association strength

            # COMMIT
            cursor.execute('UPDATE conceptgraph SET total_frequency = %s, average_proximity = %s, strength = %s WHERE id = %s' % (totalFrequency, avgProximity, strength, conceptid))

        else:                                                                       # if the row IS NOT a duplicate
            strength = calculatestrength(1, proximity)                              # calculate association strength

            print "Creating new association for %s (%s)" % (noun, association)

            totalFrequency = 1

            # COMMIT
            cursor.execute('INSERT INTO conceptgraph (noun, association_type, association, total_frequency, average_proximity, strength) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\');' % (noun, associationType, association, totalFrequency, proximity, strength))
