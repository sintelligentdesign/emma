# Name:             WordSearch
# Description:      Takes new words and searches them on tumblr, learns from the text posts.
# Section:          LEARNING
# Writes/reads:     emma.db
# Dependencies:     sqlite3, tumblrclient, parse, markovtrainer
# Dependency of:
import sqlite3 as sql

import tumblrclient
import parse
import markovtrainer

connection = sql.connect('emma.db')
cursor = connection.cursor()

def find_new_words():
    with connection:
        cursor.execute('SELECT word FROM dictionary WHERE is_new = 1;')
        newWords = cursor.fetchall()
    if newWords:
        for word in newWords:
            word = str(word[0])
            results = tumblrclient.search_for_text_posts(word)
            for result in results:
                tokenizedResult = parse.tokenize(result)
                if tokenizedResult:
                    markovtrainer.train(tokenizedResult)
                    parse.add_new_words(tokenizedResult)
            with connection:
                cursor.execute("UPDATE dictionary SET is_new = 0 WHERE word = \'%s\';" % word)