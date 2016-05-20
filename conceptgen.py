# Concept generator
import sqlite3 as sql, numpy as np

def calculatestrength(totalFreq, avgProx):
    strength = totalFreq/(np.log(avgProx) + 1)  # calculate the strength value of a concept based on its input frequency and average proximity
    return strength

connection = sql.connect('conceptgraph.db')     # connect to the concept graph SQLite database
    
def addconcept(noun, associationType, association, proximity):
    with connection:
        cursor = connection.cursor()        # get the cursor object
        
        
        # ASSOCIATION TYPE
        
        
        # ASSOCIATION
        
        
        cursor.execute('SELECT * FROM conceptgraph WHERE noun = \'%s\' AND association = \'%s\';' % (noun, association))     # check to see if the row that we want to work with is already in the database
        row = cursor.fetchone()
        
        if row != []:                                                               # if the row is a duplicate, calculate its new values and add them
            # TOTAL FREQUENCY
            totalFrequency = row[5]                                                 # get current total frequency
            totalFrequency += totalFrequency                                        # add 1 for new total frequency
            
            # AVERAGE PROXIMITY
            avgProximity = row[6]                                                   # get current average proximity
            avgProximity = (avgProximity + proximity) + totalFrequency              # calculate new average proximity
            
            # STRENGTH
            strength = calculatestrength(totalFrequency, avgProximity)              # calculate new association strength
            
            # COMMIT
            cursor.execute('INSERT INTO conceptgraph (total_frequency, avg_proximity, strength) VALUES (\'%s\', \'%s\', \'%s\');' % (totalFrequency, avgProximity, strength))
            
        else:                                                                       # if the row IS NOT a duplicate
            # ID
            # note: max id should be auto-incremented, since it's a primary key. just in case, we'll keep this around
            
            #cursor.execute('SELECT MAX(id) FROM conceptgraph;')                    # get max concept id from table
            #id = cursor.fetchone()
            #id = id[0] + 1                                                         # add 1 to get new concept id
            
            print id                                                                # todo: remove
            
            # NOUN
            cursor.execute('SELECT * FROM conceptgraph WHERE noun = \'%s\';' % noun)    # check to see if noun exists in database
            nounInDatabase = cursor.fetchall()
        
        # TOTAL FREQUENCY
        totalfrequency = 0
        
        # AVERAGE PROXIMITY
        
        
        # STRENGTH