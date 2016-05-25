# Name:             Broca's Area
# Description:      Broca's Area ... is a region in the frontal lobe of the dominant hemisphere ... with functions linked to speech production.
# Section:          REPLY
# Writes/reads:     emma.brn/conceptgraph.db
# Dependencies:     sqlite3
# Dependency of:    emma
import sqlite3 as sql, posmodelgen

connection = sql.connect('emma.brn/conceptgraph.db')        # connect to the concept graph SQLite database
cursor = connection.cursor()                                # get the cursor object

nounCodes = ['NN', 'NNS', 'NNP', 'NNPS']
verbCodes = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
adjectiveCodes = ['JJ', 'JJR', 'JJS']

def findrelatedwords(noun, associationType):
    with connection:
        SQLRequest = 'SELECT * FROM conceptgraph WHERE noun = "%s" AND association_type = ' % noun
        if associationType == 0:    # noun-noun association
            SQLRequest += "0;"
        elif associationType == 1:  # noun-verb association
            SQLRequest += "1;"
        elif associationType == 2:  # noun-adjective association
            SQLRequest += "2;"
            
        cursor.execute(SQLRequest)
        SQLReturn = cursor.fetchall()
        
        foundWords = {}
        for count in range(0, len(SQLReturn)):  # add all found associations to a dictionary, paired with their association strength
            association = SQLReturn[count]
            strength = association[7]
            association = association[3]
            foundWords[association] = strength
    return foundWords
    
def insertverbs(sentenceTemplate, importantWords, relatedVerbs, verbDictionary, inputSentenceList):
    pass