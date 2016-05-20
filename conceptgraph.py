import sqlite3 as sql, sys, numpy as np

connection = sql.connect('conceptgraph.db')     # connect to the concept graph SQLite database
    
def addconcept(noun, associationType, association, proximity):
    with connection:
        cursor = connection.cursor()        # get the cursor object
        
        # ID
        cursor.execute('SELECT MAX(id) FROM conceptgraph;')     # get max concept id from table
        id = cursor.fetchone()
        id = id[0] + 1                                          # add 1 to get new concept id
                                                                # todo: do this in pure sql
        print id                                                # todo: remove
        
        # NOUN todo: move this below dupe check
        cursor.execute('SELECT * FROM conceptgraph WHERE noun = \'%s\'' % noun)     # check to see if noun exists in database
        nounInDatabase = cursor.fetchall()
        
        
        # ASSOCIATION TYPE
        
        
        # ASSOCIATION
        
        
        cursor.execute('SELECT * FROM conceptgraph WHERE noun = \'%s\' AND association = \'%s\'' % (noun, association))     # select the row that we want to work with
        row = cursor.fetchone()
        
        if row != []:   # if the row is a duplicate, calculate its new values and add them
            # TOTAL FREQUENCY
            totalfrequency = row[5]                                                 # get current total frequency
            totalfrequency += totalfrequency                                        # add 1 for new total frequency
            # todo: commit new total frequency
            
            # AVERAGE PROXIMITY
            averageproximity = row[6]                                               # get current average proximity
            averageproximity = (averageproximity + proximity) + totalfrequency      # calculate new average proximity
            # todo: commit new average proximity
            
            # STRENGTH
            strength = totalfrequency/(np.log(averageproximity) + 1)                # calculate new association strength
            print strength
            # todo: commit new strength
            
        else:           # if the row IS NOT a duplicate
            print row   # todo: do other stuff
        
        # TOTAL FREQUENCY
        totalfrequency = 0
        
        # AVERAGE PROXIMITY
        
        
        # STRENGTH
    
addconcept("hello", 0, "friend", 1)