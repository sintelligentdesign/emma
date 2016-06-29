# -*- coding: utf-8 -*-
# Name:             Utilities
# Description:      Miscellaneous functions and vars
# Section:

import enchant
from colorama import init, Fore
init(autoreset = True)

# Auxillary functions classify POS
nounCodes = ['NN', 'NNS', 'NNP', 'NNPS']
verbCodes = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
adjectiveCodes = ['JJ', 'JJR', 'JJS']
adverbCodes = ['RB', 'RBR', 'RBS', 'RP']

# N.B. Do not use greeting terms longer than 3 words
greetingTerms = ['What\'s up', 'Hi', 'Hello', 'What up', 'Wassup', 'What is up', 'What\'s going on', 'How are you', 'Howdy', 'Hey', 'hey']

def printInfo():
    print Fore.MAGENTA + u"""
     .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.
    d88' `88b `888P"Y88bP"Y88b  `888P"Y88bP"Y88b  `P  )88b
    888ooo888  888   888   888   888   888   888   .oP"888
    888    .,  888   888   888   888   888   888  d8(  888
    `Y8bod8P' o888o o888o o888o o888o o888o o888o `Y888""8o

    ·~-.¸¸,.-~*'¯¨'*·~-.¸,.-~*'¯¨'*·~-.¸¸,.-~*'¯¨'*·~-.¸¸,.
    
            EXPANDING MODEL of MAPPED ASSOCIATIONS
                         Alpha v0.0.1
    """

d = enchant.Dict('en_US')
def spellcheck(parsedSentence):
    for count, row in enumerate(parsedSentence):
        word = row[0]
        if d.check(word) == False:
            # todo: put what we want to do for words that flag the spell checker here
            print Fore.RED + "Found possible mispelled word: \'%s\'" % word
    return parsedSentence