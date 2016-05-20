# Concept generator
import sqlite3 as sql, numpy as np

def calculatestrength(totalFreq, avgProx):
    strength = totalFreq/(np.log(avgProx) + 1)  # calculate the strength value of a concept based on its input frequency and average proximity
    return strength

connection = sql.connect('conceptgraph.db')     # connect to the concept graph SQLite database
    
def addconcept(noun, associationType, association, proximity):
    noun = noun.title()
    association = association.title()
    with connection:
        cursor = connection.cursor()            # get the cursor object
        
        cursor.execute('SELECT * FROM conceptgraph WHERE noun = \'%s\' AND association = \'%s\';' % (noun, association))     # check to see if the row that we want to work with is already in the database
        row = cursor.fetchone()
        
        if row != None:                                                             # if the row is a duplicate, calculate its new values and add them
            print "Adding new values to existing concept for association %s, %s" % (noun, association)
            
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
            cursor.execute('UPDATE conceptgraph SET total_frequency = %s, avg_proximity = %s, strength = %s WHERE id = %s' % (totalFrequency, avgProximity, strength, conceptid))
            
        else:                                                                       # if the row IS NOT a duplicate
            strength = calculatestrength(1, proximity)                               # calculate association strength
            print "Creating new concept for association %s, %s" % (noun, association)
            
            totalFrequency = 1
            
            # COMMIT
            cursor.execute('INSERT INTO conceptgraph (noun, association_type, association, total_frequency, avg_proximity, strength) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\');' % (noun, associationType, association, totalFrequency, proximity, strength))