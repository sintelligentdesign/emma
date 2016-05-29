# Name:             Input Parser
# Description:      Tokenizes input and adds new words and their information into brain.db/dictionary
# Section:          LEARNING
# Writes/reads:     emma.brn/conceptgraph.db
# Dependencies:     pattern.en, sqlite3
# Dependency of:
import pattern.en as pattern
import sqlite3 as sql

def tokenize(text):
    pattern.pprint(pattern.parse(text, True, True, True, True, True))

    taggedText = pattern.parse(text, True, True, True, True, True).split()
    for taggedSentence in taggedText:
        posSentence = []
        chunkSeries = []
        lemmaSentence = []
        for taggedWord in taggedSentence:
            posSentence.append(taggedWord[1])
            chunkSeries.append(taggedWord[2])
            lemmaSentence.append(taggedWord[5])
        tagList = zip(lemmaSentence, posSentence, chunkSeries)
        print "Zipped Tag Sentence: %s\n" % tagList
    return tagList

tokenize("I made a pretty whistle out of wood. It sounds good.")
tokenize("I'm back.")
tokenize("He ate an apple. His friend watched longingly.")

def check_words_against_brain():
    # todo: error checking: see if we agree with how words are used in the sentence. If not, assume our understanding of the word is wrong.
    pass

# connect to the concept graph SQLite database
connection = sql.connect('brain.db')
cursor = connection.cursor()
def add_new_words(posSentence, lemmaSentence):
    with connection:
        cursor.execute('SELECT * FROM dictionary;')
        SQLReturn = cursor.fetchall()
    storedLemata = []
    for row in SQLReturn:
        storedLemata.append(row[0])
    for count, lemma in enumerate(lemmaSentence):
        if lemma not in storedLemata:       # instead of checking to see if lemma == '.', we just add '.' as a banned word in the dictionary
            # todo: score capitalization
            capitalizationScore = "000000"
            pos = posSentence[count]
            with connection:
                print 'Learned new word! (%s)' % lemma
                cursor.execute('INSERT INTO dictionary VALUES (\'%s\', \'%s\', %s, 1, 0);' % (lemma, pos, capitalizationScore))

add_new_words(['PRP', 'VBD', 'DT', 'JJ', 'NN', 'IN', 'IN', 'NN'], ['i', 'make', 'a', 'pretty', 'whistle', 'out', 'of', 'wood'])
add_new_words(['PRP', 'VBD', 'DT', 'NN', '.'], ['he', 'eat', 'an', 'apple', '.'])
add_new_words(['PRP$', 'NN', 'VBD', 'RB', '.'], ['his', 'friend', 'watch', 'longingly', '.'])