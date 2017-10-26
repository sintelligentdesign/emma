import numpy as np
import re

import sqlite3 as sql

import logging
import misc

E = np.exp(1)
RANKING_CONSTANT = 3.19722457734
def calculate_new_weight(currentWeight):
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
            cursor.execute('SELECT id FROM dictionary WHERE word = "{0}" AND part_of_speech = "{1}";'.format(word.lemma, word.partOfSpeech))
            wordID = cursor.fetchone()
            cursor.execute('SELECT id FROM dictionary WHERE word = "{0}" AND part_of_speech = "{1}";'.format(word.lemma, word.partOfSpeech))
            targetID = cursor.fetchone()

        # Check to see if an association exists