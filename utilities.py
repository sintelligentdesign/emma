# Name:             Utilities
# Description:      Miscellaneous functions and vars
# Section:
import sqlite3 as sql

connection = sql.connect('emma.db')
cursor = connection.cursor()

# Auxillary functions classify POS
nounCodes = ['NN', 'NNS', 'NNP', 'NNPS']
verbCodes = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
adjectiveCodes = ['JJ', 'JJR', 'JJS']
adverbCodes = ['RB', 'RBR', 'RBS'] # should this include RP

def find_related_words(word):
    relatedWords = []
    relatedWord = ()
    with connection:
        cursor.execute('SELECT target, association_type, weight FROM associationmodel WHERE word = \'%s\';' % word)
        SQLReturn = cursor.fetchall()
    for row in SQLReturn:
        relatedWord = (row[0], row[1], row[2])
        if relatedWord != ():
            relatedWords.append(relatedWord)
    # todo: remove dupes
    return relatedWords