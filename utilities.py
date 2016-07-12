# -*- coding: utf-8 -*-
# Name:             Utilities
# Description:      Miscellaneous functions and vars
# Section:

from colorama import init, Fore
init(autoreset = True)

# Auxillary functions classify POS
nounCodes = ['NN', 'NNS', 'NNP', 'NNPS']
verbCodes = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
adjectiveCodes = ['JJ', 'JJR', 'JJS']
adverbCodes = ['RB', 'RBR', 'RBS', 'RP']