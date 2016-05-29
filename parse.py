# Name:             Input Parser
# Description:      Tokenizes input and adds new words and their information into brain.db/dictionary
# Section:          LEARNING
# Writes/reads:     emma.brn/conceptgraph.db
# Dependencies:     pattern.en, sqlite3, markovtrainer
# Dependency of:
import pattern.en as pattern
import sqlite3 as sql

import markovtrainer

def tokenize(text):
    #pattern.pprint(pattern.parse(text, True, True, True, True, True))

    taggedText = pattern.parse(text, True, True, True, True, True).split()
    for taggedSentence in taggedText:
        posSentence = []
        chunkSeries = []
        lemmaSentence = []
        for taggedWord in taggedSentence:
            posSentence.append(taggedWord[1])
            chunkSeries.append(taggedWord[2])
            lemmaSentence.append(taggedWord[5])
        wordInfo = zip(lemmaSentence, posSentence, chunkSeries)
    return wordInfo

def check_words_against_brain():
    # todo: error checking: see if we agree with how words are used in the sentence. If not, assume our understanding of the word is wrong.
    pass

# connect to the concept graph SQLite database
connection = sql.connect('emma.db')
cursor = connection.cursor()
def add_new_words(wordInfo):
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
            capitalizationScore = "000000"
            print 'Learned new word! (%s)' % lemma
            with connection:
                cursor.execute('INSERT INTO dictionary VALUES (\'%s\', \'%s\', %s, 1, 0);' % (lemma, pos, capitalizationScore))

testSet = ["I made a pretty whistle out of wood.", "It sounds good.", "I'm back. He ate an apple.", "His friend watched longingly."]
for sentence in testSet:
    markovtrainer.train(tokenize(sentence))
    add_new_words(tokenize(sentence))