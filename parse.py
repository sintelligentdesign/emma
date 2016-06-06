# Name:             Input Parser
# Description:      Tokenizes input and adds new words and their information into brain.db/dictionary
# Section:          LEARNING
import pattern.en
import sqlite3 as sql

import markovtrainer

def tokenize(text):
    print "Tokenizing sentence \"%s\"." % text
    pattern.en.pprint(pattern.en.parse(text, True, True, True, True, True))

    taggedText = pattern.en.parse(text, True, True, True, True, True).split()
    for taggedSentence in taggedText:
        posSentence = []
        chunkSeries = []
        lemmaSentence = []
        subObj =[]
        
        # todo: determine important words
        
        for taggedWord in taggedSentence:
            posSentence.append(taggedWord[1])
            chunkSeries.append(taggedWord[2])
            lemmaSentence.append(taggedWord[5])
            subObj.append(taggedWord[4])
        wordInfo = zip(lemmaSentence, posSentence, chunkSeries, subObj)
        return wordInfo

def check_words_against_brain():
    # todo: error checking: see if we agree with how words are used in the sentence. If not, assume our understanding of the word is wrong.
    pass

# connect to the concept graph SQLite database
connection = sql.connect('emma.db')
cursor = connection.cursor()
# todo: change function name to consume()?
def add_new_words(wordInfo):
    print "Reading sentence..."
    with connection:
        cursor.execute('SELECT * FROM dictionary;')
        SQLReturn = cursor.fetchall()

    storedLemata = []
    for row in SQLReturn:
        storedLemata.append(row[0])

    for count, item in enumerate(wordInfo):
        lemma = item[0]
        pos = item[1]

        if lemma not in storedLemata:       # instead of checking to see if lemma == '.', we just add '.' as a banned word in the dictionary
            print 'Learned new word: (%s)!' % lemma
            with connection:
                cursor.execute("INSERT INTO dictionary VALUES (\"%s\", \"%s\", 1, 0);" % (lemma, pos))