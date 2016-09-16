# Name:             Association Trainer
# Description:      Finds and adds associations to Emma's association model
# Section:          LEARNING
import numpy as np
import re

import sqlite3 as sql
from colorama import init, Fore
init(autoreset = True)

import utilities

connection = sql.connect("emma.db")
cursor = connection.cursor()

def find_associations(parsedSentence):
    print parsedSentence        # todo: Remove debug print statement
    for count, word in enumerate(parsedSentence):

        ## Look for keywords
        if count != 0 and count - 1 != len(sentence):       # If this doesn't work __I will scream__

            # Make lists out of the words before and after the word that we're on
            wordsBackward = sentence[0:count]
            wordsForeward = sentence[count + 1:-1]

            # Begin by looking for the word "be"
            if word[0] == u"be":
                if "NP" in sentence[count] - 1: 
            # Now look for the word "has"
            if word[0] == u"has":
                pass

            ## Look for orders of word types
            # todo