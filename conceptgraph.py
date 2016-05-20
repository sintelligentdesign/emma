import sqlite3 as sql
import sys

connection = sql.connect('conceptgraph.db') # connect to the concept graph SQLite database
    
def addconcept(noun, associationType, association, proximity):
    with connection:
        cursor = connection.cursor()        # get the cursor object
        
        
        # ID
        cursor.execute('SELECT MAX(id) FROM conceptgraph;') # get max concept id from table
        id = cursor.fetchone()
        id = id[0] + 1                                      # add 1 to get new concept id
                                                            # todo: do this in pure sql
        print id                                            # todo: remove
        
        # NOUN
        
        
        # ASSOCIATION TYPE
        
        
        # ASSOCIATION
        
        
        # TOTAL FREQUENCY
        
        
        # AVERAGE PROXIMITY
        
        
        # STRENGTH
        
        
    except lite.Error, e:
        if connection:
            connection.rollback()
        
        print "Error %s:" % e.args[0]
        sys.exit (1)
    
addconcept("hello", 0, "friend", 1) #todo: remove