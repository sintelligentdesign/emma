import numpy as np

import logging

def add_association(word, type, target):

E = np.exp(1)
RANKING_CONSTANT = 3.19722457734
def calculate_new_weight(currentWeight):
    """Take an association's weight and increase it"""
    # TODO: This function should be able to decrease weights too
    # Don't let weights be exactly 1 because this breaks stuff
    if currentWeight == 1:
        currentWeight = 0.999999999994
    
    # Transform the weight back into the number of occurances of the word
    occurances = np.log(currentWeight/(1-currentWeight))+RANKING_CONSTANT
    occurances += 1

    # Re-calculate weight
    newWeight = 1/(1+E**(occurances-RANKING_CONSTANT))
    return newWeight