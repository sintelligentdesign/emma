# Concept generator
import sqlite3 as sql, numpy as np

def calculatestrength(totalFreq, avgProx):
    strength = totalFreq/(np.log(avgProx) + 1)  # calculate the strength value of a concept based on its input frequency and average proximity
    return strength

connection = sql.connect('emma.brn/conceptgraph.db')     # connect to the concept graph SQLite database
    
def addconcept(noun, associationType, association, proximity):
    with connection:
        cursor = connection.cursor()            # get the cursor object
        
        cursor.execute('SELECT DISTINCT noun FROM conceptgraph;')   # check to see if Emma has seen this word before
        fullWordList = cursor.fetchall()
        if fullWordList:
            for count in range(0, len(fullWordList)):
                oldWords = fullWordList[count]
                if noun in oldWords[0]:
                    print "Learned new word (%s)!" % noun
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