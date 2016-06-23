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

def printInfo():
    print Fore.MAGENTA + u"""
     .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.
    d88' `88b `888P"Y88bP"Y88b  `888P"Y88bP"Y88b  `P  )88b
    888ooo888  888   888   888   888   888   888   .oP"888
    888    .,  888   888   888   888   888   888  d8(  888
    `Y8bod8P' o888o o888o o888o o888o o888o o888o `Y888""8o

    ·~-.¸¸,.-~*'¯¨'*·~-.¸,.-~*'¯¨'*·~-.¸¸,.-~*'¯¨'*·~-.¸¸,.
    
            EXPANDING MODEL of MAPPED ASSOCIATIONS
                           Pre-Alpha
    """

d = enchant.Dict('en_US')
def spellcheck(parsedSentence):
    for count, row in enumerate(parsedSentence):
        word = row[0]
        if d.check(word) == False:
            userPrompt = raw_input(Fore.RED + "Possible mispelled word found: \'%s\'. Add to dictionary? y/n: " % word)
            if "y" in userPrompt.lower():
                d.add(word)
            elif "n" in userPrompt.lower():
                newWord = d.suggest(word)
                userPrompt = raw_input(Fore.RED + "Replace \'%s\' with my best guess at its correct spelling, \'%s\'? y/n: " % (word, newWord[0]))
                if "y" in userPrompt.lower():
                    print Fore.GREEN + "Replacing \'%s\' with \'%s\'" % (word, newWord[0])
                    parsedSentence[count] = [newWord[0], row[1], row[2], row[3]]
    return parsedSentence