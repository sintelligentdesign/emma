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