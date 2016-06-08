# Name:             Words API Client
# Description:      Communicates with Words API via Mashape and executes related functions
# Section:          LEARNING
import unirest

import apikeys

def get_relation(word, relationType):
    # todo: what do we do with n-grams that are returned?
    #       we should be able input a list for relationType and get a list of results in return to minimize API calls
    # Relations are:
    
    # hasParts      (house has door, floor, window)     return IS-PART-OF input
    # partOf        (finger is part of mitt, hand)      input IS-PART-OF return
    
    # inCategory    (string theory is in physics)       input IS-RELATED-TO return
    # similarTo     (happy is similar to bliss, bright) return IS-RELATED-TO input
    
    # typeOf        (rose is type of bush, flower)      input IS-A return
    # instanceOf    (einstein is instance of physicist) input IS-A return
    # hasTypes      (cat has tiger, housecat, lion)     return IS-A input
    
    url = 'https://wordsapiv1.p.mashape.com/words/' + word
    response = unirest.get(url, headers={"X-Mashape-Key": apikeys.wordsEnvironmentKey, "Accept": "application/json"})
    response = response.body
    results = response["results"]
    
    relations = []
    for result in results:
        if relationType in result.keys():
            relation = result[relationType]
            relations.append(relation)
    
    return relations