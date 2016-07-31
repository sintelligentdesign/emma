# Name:             Input Parser
# Description:      Tokenizes input and adds new words and their information into brain.db/dictionary
# Section:          LEARNING
import re

import pattern.en
import sqlite3 as sql
from colorama import init, Fore
init(autoreset = True)

import utilities
import settings

connection = sql.connect('emma.db')
cursor = connection.cursor()

def tokenize(text):
    if text[-1] not in [u"!", u"?", "."]: text += u"."
    text = translate_netspeak(text)

    print "Tokenizing message..."
    if settings.option('general', 'verboseLogging'): pattern.en.pprint(pattern.en.parse(text, True, True, True, True, True))
    taggedText = pattern.en.parse(text, True, True, True, True, True).split()
    
    parsedMessage = []
    for count, taggedSentence in enumerate(taggedText):
        finalize_sentence(taggedSentence)

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

def translate_netspeak(text):
    # Turn internet abbreviations into proper English
    text = text.split(' ')
    txtDict = {
        u'aight': [u'alright'],
        u'btw': [u'by', u'the', u'way'],
        u'cn': [u'can'],
        u'gonna': [u'going', u'to'],
        u'im': [u'I\'m'],
        u'imo': [u'in', u'my', u'opinion'],
        u'lemme': [u'let', u'me'],
        u'n': [u'and'],
        u'obv': [u'obviously'],
        u'omg': [u'oh', u'my', u'god'],
        u'r': [u'are'],
        u'tbh': [u'to', u'be', u'honest'],
        u'u': [u'you'],
        u'ur': [u'your'],
        u'yea': [u'yeah']
    }

    decodedText = []
    for word in text:
        if re.sub(r'[\d\s\W]', "", word.lower()) in txtDict.keys():
            punctuation = u""
            if word[-1] in [u'.', u',', u'!', u'?']: punctuation = word[-1]     # Take note of punctuation so that we can put it back in later
            
            print Fore.GREEN + u"Translating \"%s\" from txt speak..." % word
            replacementWord = txtDict[re.sub(r'[\d\s\W]', "", word.lower())]

            if punctuation != "": replacementWord[-1] += punctuation

            decodedText.extend(replacementWord)
        else: decodedText.append(word)
    return ' '.join(decodedText)

bannedWords = []
with connection:
    cursor.execute('SELECT word FROM dictionary WHERE is_banned = 1')
    for word in cursor.fetchall(): bannedWords.append(word[0])
def finalize_sentence(taggedSentence):
    rowsToRemove = []
    for count, taggedWord in enumerate(taggedSentence):
        if count != 0: prevWord = taggedSentence[count - 1]
        if count != len(taggedSentence) - 1: nextWord = taggedSentence[count + 1]
        
        if taggedWord[5] in [u"n\'t", u"n\u2019t", u"n\u2018t"]:
            print Fore.GREEN + "Replacing \"n\'t\" with \"not\"..."
            taggedWord[5] = u"not"
        elif taggedWord[5] in [u"\'", u"\u2019", u"\u2018"] and prevWord and nextWord:
            print Fore.GREEN + "Joining \"%s\" and \"%s\"..." % (prevWord[5], nextWord[0])
            prevWord[5] = prevWord[5] + "\'" + nextWord[0]
            rowsToRemove.append(taggedWord)
            rowsToRemove.append(nextWord)
        elif taggedWord[5] in [u"\'s'", u"\u2019s", u"\u2018s"] or taggedWord[1] == "POS" and prevWord:
            print Fore.GREEN + "Appending \"\'s\" to \"%s\"..." % prevWord[5]
            prevWord[5] = prevWord[5] + u"\'s"
            rowsToRemove.append(taggedWord)
        elif taggedWord[1] in [u"\"", u"FW", u":", u".", u"(", u")"] or taggedWord[5] in [u",", u"\u007c", u"\u2015", u"#", u"[", u"]", u"(", u")", u"{", u"}" u"\u2026", u"<", u">"]:
            print Fore.GREEN + "Removing \"%s\"" % taggedWord[1]
            rowsToRemove.append(taggedWord)
        elif taggedWord[5] in bannedWords:
            print Fore.GREEN + "Removing naughty word \"%s\"" % taggedWord[1]
            rowsToRemove.append(taggedWord)

    if rowsToRemove:
        for row in rowsToRemove:
            if row in taggedSentence: taggedSentence.remove(row)

    return taggedSentence

def add_new_words(parsedSentence):
    # todo: make use of synonym column in emma's dictionary
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

        if lemma not in storedLemata and lemma not in wordsLeft and lemma not in addedWords and lemma not in bannedWords and lemma.isnumeric() == False:
            print Fore.MAGENTA + u"Learned new word: \'%s\'!" % lemma
            addedWords.append(lemma)
            with connection:
                cursor.execute("INSERT INTO dictionary VALUES (\"%s\", \"%s\", 1, 0, null);" % (re.escape(lemma), pos))

greetingTerms = [[u'what\'s', u'up'], [u'hi'], [u'yo'], [u'hiya'], [u'hello'], [u'what', u'up'], [u'wassup'], [u'what', u'is', u'up'], [u'what\'s', u'going', u'on'], [u'how', u'are', u'you'], [u'howdy'], [u'hey'], [u'good', u'morning'], [u'good', u'evening'], [u'good', u'afternoon']]
def determine_intent(parsedSentence):
    intent = {'declarative': False, 'interrogative': False, 'greeting': False}
    message = []
    for word in parsedSentence: message.append(word[0])

    # Greeting pass
    for greeting in greetingTerms:
        match = re.match(' '.join(greeting), ' '.join(message[0:3]))
        if match: intent['greeting'] = True

    # Interrogative pass
    print parsedSentence
    if len(parsedSentence) > 1:
        if parsedSentence[0][1] in ("WDT", "WP", "WP$", "WRB") or parsedSentence[1][1] in (u'be') or parsedSentence[-1][0] == "?": intent['interrogative'] = True

    # Declarative pass
    if intent['interrogative'] == False:
        # If we have a greeting, check to see if the sentence is compound
        if intent['greeting']:
            if "," in message[:5]: intent['declarative'] = True
        else: intent['declarative'] = True

    return intent