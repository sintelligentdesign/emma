# -*- coding: utf-8 -*-
# Name:             Input Parser
# Description:      Tokenizes input and adds new words and their information into brain.db/dictionary
# Section:          LEARNING
import re

import pattern.en
import sqlite3 as sql
from unidecode import unidecode

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
        
        for count, taggedWord in enumerate(taggedSentence):
            if taggedWord[5] in ["n\'t", "n’t".decode('utf-8')]:
                taggedWord[5] = "not"
            elif taggedWord[5] in ["\'", "’".decode('utf-8')]:
                if count != len(taggedSentence) - 1:
                    prevWord = taggedSentence[count - 1]
                    nextWord = taggedSentence[count + 1]
                    prevWord[5] = prevWord[5] + "\'" + nextWord[0]
                    taggedSentence.remove(taggedWord)
                    taggedSentence.remove(nextWord)
            elif taggedWord[5] == "’s" or taggedWord[1] == "POS":
                prevWord = taggedSentence[count - 1]
                prevWord[5] = prevWord[5] + "\'s"
                taggedSentence.remove(taggedWord)
        
        for taggedWord in taggedSentence:
            if taggedWord[1] != "POS":      # Filter out possesive "'s'"
                posSentence.append(taggedWord[1])
                chunkSeries.append(taggedWord[2])
                lemmaSentence.append(taggedWord[5])
                subObj.append(taggedWord[4])
        wordPackage = zip(lemmaSentence, posSentence, chunkSeries, subObj)
        return wordPackage

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

        if re.escape(lemma) not in storedLemata and "\"" not in pos and lemma.isnumeric() == False and pos != "FW":
            print 'Learned new word: (%s)!' % lemma
            with connection:
                cursor.execute("INSERT INTO dictionary VALUES (\"%s\", \"%s\", 1, 0);" % (re.escape(lemma), pos))