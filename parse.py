# Name:             Input Parser
# Description:      Tokenizes input and adds new words and their information into brain.db/dictionary
# Section:          LEARNING
import pattern.en
import sqlite3 as sql

import markovtrainer

def tokenize(text):
    print u"Tokenizing sentence \"%s\"." % text
    pattern.en.pprint(pattern.en.parse(text, True, True, True, True, True))
    taggedText = pattern.en.parse(text, True, True, True, True, True).split()

    
    for taggedSentence in taggedText:
        posSentence = []
        chunkSeries = []
        lemmaSentence = []
        subObj =[]
        
        rowsToRemove = []
        for count, taggedWord in enumerate(taggedSentence):
            if taggedWord[5] in [u"n\'t", u"n\u2019t", u"n\u2018t"]:
                taggedWord[5] = "not"
            elif taggedWord[5] in [u"\'", u"\u2019", u"\u2018"]:
                if count != len(taggedSentence) - 1:
                    prevWord = taggedSentence[count - 1]
                    nextWord = taggedSentence[count + 1]
                    prevWord[5] = prevWord[5] + "\'" + nextWord[0]
                    rowsToRemove.append(taggedWord)
                    rowsToRemove.append(nextWord)
            elif taggedWord[5] in [u"\'s'", u"\u2019s", u"\u2018s"] or taggedWord[1] == "POS":
                prevWord = taggedSentence[count - 1]
                prevWord[5] = prevWord[5] + u"\'s"
                rowsToRemove.append(taggedWord)
            elif taggedWord[1] == u"\"" or taggedWord[5] in [u",", u"\u007c", u"\u2015", u"#", u"[", u"]", u"(", u")" u"\u2026", u"<", u">"]:
                rowsToRemove.append(taggedWord)

        if rowsToRemove:
            print "Removing garbage..."
            for row in rowsToRemove:
                taggedSentence.remove(row)
                print u"Removed %s." % row[0]
        
        for taggedWord in taggedSentence:
            posSentence.append(taggedWord[1])
            chunkSeries.append(taggedWord[2])
            lemmaSentence.append(taggedWord[5])
            subObj.append(taggedWord[4])
        wordPackage = zip(lemmaSentence, posSentence, chunkSeries, subObj)
        parsedSentence = []
        for package in wordPackage:
            parsedSentence.append(list(package))
        return parsedSentence

connection = sql.connect('emma.db')
cursor = connection.cursor()
def add_new_words(wordInfo):
    print "Reading sentence..."
    with connection:
        cursor.execute('SELECT * FROM dictionary;')
        SQLReturn = cursor.fetchall()

    storedLemata = []
    for row in SQLReturn:
        lemma = row[0]
        storedLemata.append(lemma)

    addedWords = []
    for count, item in enumerate(wordInfo):
        lemma = item[0]
        pos = item[1]

        wordsLeft = wordInfo[-(len(wordInfo) - count):len(wordInfo) - 1]

        if lemma not in storedLemata and lemma not in wordsLeft and lemma not in addedWords and lemma.isnumeric() == False and pos != "FW":
            print u"Learned new word: (%s)!" % lemma
            addedWords.append(lemma)
            with connection:
                cursor.execute("INSERT INTO dictionary VALUES (\"%s\", \"%s\", 1, 0);" % (lemma, pos))