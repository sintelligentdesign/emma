# Name:             Input Parser
# Description:      Tokenizes input and adds new words and their information into brain.db/dictionary
# Section:          LEARNING
import pattern.en
import sqlite3 as sql
from colorama import init, Fore
init(autoreset = True)

import markovtrainer
from config import console, database

def tokenize(text):
    print "Tokenizing message..."
    if console['verboseLogging']: pattern.en.pprint(pattern.en.parse(text, True, True, True, True, True))
    taggedText = pattern.en.parse(text, True, True, True, True, True).split()
    
    parsedMessage = []
    for count, taggedSentence in enumerate(taggedText):
        if console['verboseLogging']: print "Reading sentence no. %d..." % (count + 1)
        if console['verboseLogging']: print "Checking for conjunctions and illegal characters..."
        rowsToRemove = []
        for count, taggedWord in enumerate(taggedSentence):
            if taggedWord[5] in [u"n\'t", u"n\u2019t", u"n\u2018t"]:
                print Fore.GREEN + "Replacing \"n\'t\" with not..."
                taggedWord[5] = u"not"
            elif taggedWord[5] in [u"\'", u"\u2019", u"\u2018"]:
                if count != len(taggedSentence) - 1:
                    prevWord = taggedSentence[count - 1]
                    nextWord = taggedSentence[count + 1]
                    print Fore.GREEN + "Joining \'%s\' and \'%s\'..." % (prevWord[5], nextWord[0])
                    prevWord[5] = prevWord[5] + "\'" + nextWord[0]
                    rowsToRemove.append(taggedWord)
                    rowsToRemove.append(nextWord)
            elif taggedWord[5] in [u"\'s'", u"\u2019s", u"\u2018s"] or taggedWord[1] == "POS":
                prevWord = taggedSentence[count - 1]
                print Fore.GREEN + "Appending \"\'s\" to \'%s\'..." % prevWord[5]
                prevWord[5] = prevWord[5] + u"\'s"
                rowsToRemove.append(taggedWord)
            elif taggedWord[1] == u"\"" or taggedWord[5] in [u",", u"\u007c", u"\u2015", u"#", u"[", u"]", u"(", u")" u"\u2026", u"<", u">"]:
                rowsToRemove.append(taggedWord)

        if rowsToRemove:
            print Fore.GREEN + "Tidying up..."
            for row in rowsToRemove:
                if row in taggedSentence:
                    taggedSentence.remove(row)
                    print Fore.GREEN + u"Removed %s." % row[0]
        
        posSentence = []
        chunkSeries = []
        lemmaSentence = []
        subObj =[]
        for taggedWord in taggedSentence:
            posSentence.append(taggedWord[1])
            chunkSeries.append(taggedWord[2])
            lemmaSentence.append(taggedWord[5])
            subObj.append(taggedWord[4])
        parsedSentence = zip(lemmaSentence, posSentence, chunkSeries, subObj)
        for count, word in enumerate(parsedSentence):
            parsedSentence[count] = list(word)
        parsedMessage.append(parsedSentence)
    return parsedMessage

connection = sql.connect(database['path'])
cursor = connection.cursor()
def add_new_words(parsedSentence):
    if console['verboseLogging']: print "Looking for new words..."
    with connection:
        cursor.execute('SELECT * FROM dictionary;')
        SQLReturn = cursor.fetchall()

    storedLemata = []
    for row in SQLReturn:
        lemma = row[0]
        storedLemata.append(lemma)

    addedWords = []
    for count, item in enumerate(parsedSentence):
        lemma = item[0]
        pos = item[1]

        wordsLeft = parsedSentence[-(len(parsedSentence) - count):len(parsedSentence) - 1]

        if lemma not in storedLemata and lemma not in wordsLeft and lemma not in addedWords and lemma not in pattern.en.wordlist.PROFANITY and lemma.isnumeric() == False and pos != "FW":
            print Fore.MAGENTA + u"Learned new word: (%s)!" % lemma
            addedWords.append(lemma)
            with connection:
                cursor.execute("INSERT INTO dictionary VALUES (\"%s\", \"%s\", 1, 0);" % (lemma, pos))