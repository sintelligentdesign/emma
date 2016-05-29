# Name:             WordSearch
# Description:      Takes new words and searches them on tumblr, learns from the texts posts.
# Section:          LEARNING
# Writes/reads:     emma.db
# Dependencies:     sqlite3, tumblrclient
# Dependency of:
import sqlite3 as sql

import tumblrclient

connection = sql.connect('emma.db')
cursor = connection.cursor()

def find_new_words():
    with connection:
        cursor.executescript("""
            SELECT word FROM dictionary WHERE is_new = 1;
            UPDATE dictionary SET is_new = 0 WHERE is_new = 1;
        """)
        newWords = cursor.fetchall()
    if newWords:
        for word in newWords:
            word = str(word[0])
            print tumblrclient.search_for_text_posts(word)
            # todo: do stuff with this