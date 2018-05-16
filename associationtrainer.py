import numpy as np
import re

import sqlite3 as sql

import logging
import misc

E = np.exp(1)
RANKING_CONSTANT = 3.19722457734
def calculate_weight(currentWeight):
    """Take an association's weight and increase it"""
    # TODO: This function should be able to decrease weights too
    # If the weight is 1, we cannot increase it further and transforming it back into number of occurances would result in a division by 0
    if currentWeight == 1:
        return 1
    else:
        # Transform the weight back into the number of occurances of the word and add 1
        occurances = np.log(currentWeight/(1-currentWeight))+RANKING_CONSTANT
        occurances += 1

        # Re-calculate weight
        newWeight = 1/(1+E**(occurances-RANKING_CONSTANT))
        return newWeight

connection = sql.connect('emma.db')
connection.text_factory = str
cursor = connection.cursor()

def train_association(word, associationType, target):
    """Add or modify an association in the Association Model"""
    # We want to ignore associations with self, so
    if word != target:
        # Get the IDs of the word and the target
        with connection:
            cursor.execute('SELECT id FROM dictionary WHERE word = ? AND part_of_speech = ?;', (word.lemma, word.type))
            wordID = cursor.fetchone()[0]
            cursor.execute('SELECT id FROM dictionary WHERE word = ? AND part_of_speech = ?;', (target.lemma, target.type))
            targetID = cursor.fetchone()[0]

        # Check to see if an association exists
        with connection:
            cursor.execute('SELECT * FROM associationmodel WHERE word_id = ? AND target_id = ?;', (wordID, targetID))
            result = cursor.fetchone()
            if result:
                # Update an existing association
                logging.info("Strengthening association {0} {1} {2}".format(word.lemma, associationType, target.lemma))
                weight = calculate_weight(result[3])
                cursor.execute('UPDATE associationmodel SET weight = ? WHERE word_id = ? AND target_id = ?;', (weight, wordID, targetID))
            else:
                # Add a new association
                logging.info("Found new association {0} {1} {2}".format(word.lemma, associationType, target.lemma))
                # This is the weight that would be caluclated for any new association, so we'll just declare it
                weight = 0.0999999999997
                cursor.execute('INSERT INTO associationmodel VALUES (?, ?, ?, ?);', (wordID, associationType, targetID, weight))
                

def find_associations(message):
    """Use pattern recognition to learn from a Message object"""
    # """
    # We're interested in the following patterns to start:
    # VP NP
    # NP VP NP
    # NP VP ADJP
    # NP VP NP ADJP
    # """
    for sentence in message.sentences:
        # Don't learn from questions
        if sentence.words[-1] != u'?':
            logging.debug("Sentence chunks: {0}".format(sentence.chunks))

            # Scan through the sentence to find patterns of chunks that we're interested in
            searchRange = 3

            for i in range(0, len(sentence.chunks)):
                searchEndBound = i + searchRange

                # Take a slice of the sentence
                logging.debug("Search bounds: [{0}:{1}]".format(i, searchEndBound))
                searchSlice = sentence.chunks[i:searchEndBound]
                logging.debug("Search slice: {0}".format(searchSlice))

                # Check the chunk types
                chunkTypes = []
                for chunk in searchSlice:
                    chunkTypes.append(chunk.type)

                # Look for patterns that suggest associations
                if chunkTypes == [u"NP", u"VP", u"ADJP"]:
                    # "Dogs are cute", "The dog is adorable", "Dogs are very fluffy"
                    logging.debug("Found NP VP ADJP! {0}".format(searchSlice))

                    if searchSlice[1].head.lemma == u"be":
                        train_association(searchSlice[0].head, 'HAS-PROPERTY', searchSlice[2].head)

        else:
            logging.debug("Sentence is a question. Skipping learning...")