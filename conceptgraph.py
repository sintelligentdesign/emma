import sqlite3 as sql
import sys

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
        
        # NOUN
        cursor.execute('SELECT * FROM conceptgraph WHERE noun = \'%s\'' % noun)     # check to see if noun exists in database
        nounInDatabase = cursor.fetchall()
        
        
        # ASSOCIATION TYPE
        
        
        # ASSOCIATION
        
        
        cursor.execute('SELECT * FROM conceptgraph WHERE noun = \'%s\' AND association = \'%s\'' % (noun, association))     # select the row that we want to work with
        row = cursor.fetchall()
        if row != []:   # if the row is a duplicate
            print row   # todo: do stuff
        else:           # if the row IS NOT a duplicate
            print row   # todo: do other stuff
        
        # TOTAL FREQUENCY
        totalfrequency = 0
        
        # AVERAGE PROXIMITY
        
        
        # STRENGTH
    
addconcept("hello", 0, "friend", 1)