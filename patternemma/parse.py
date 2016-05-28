import pattern.en
import sqlite3 as sql

def tokenize(text):
    pattern.en.pprint(pattern.en.parse(text, True, True, True, True, True))

    taggedText = pattern.en.parse(text, True, True, True, True, True).split()
    for taggedSentence in taggedText:
        posSentence = []
        chunkSeries = []
        lemmaSentence = []
        for taggedWord in taggedSentence:
            posSentence.append(taggedWord[1])
            chunkSeries.append(taggedWord[2])
            lemmaSentence.append(taggedWord[5])
        print "Parts of Speech: %s" % posSentence
        print "Sentence Chumks: %s" % chunkSeries
        print "Lemma: %s\n" % lemmaSentence
    return posSentence
    return chunkSeries
    return lemmaSentence

tokenize("I made a pretty whistle out of wood. It sounds good.")
tokenize("I am back.")
tokenize("He ate an apple. His friend watched longingly.")

def check_words_against_brain():
    # todo: error checking: see if we agree with how words are used in the sentence. If not, assume our understanding of the word is wrong.
    pass

# connect to the concept graph SQLite database
connection = sql.connect('emma.brn/conceptgraph.db')
cursor = connection.cursor()
def add_new_words(posSentence, lemmaSentence):
    with connection:
        cursor.execute('SELET * FROM dictionary')
        SQLReturn = cursor.fetchall()
    storedWords = []
    for row in SQLReturn:
        storedWords.append(row[0])
    for word in lemmaSentence:
        if word not == "." and word not in storedWords:
            # todo: get information about part of speech and score capitalization
            with connection:
                cursor.execute('INSERT INTO dictionary VALUES (word, pos, capitalizationScore, 1, 0)')