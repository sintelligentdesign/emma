# Name:             Configuration File
# Description:      Emma's "control panel"
# Section:
# Writes/reads:
# Dependencies:
# Dependency of:

# Auxillary functions classify POS
def nounCodes(): return ['NN', 'NNS', 'NNP', 'NNPS']
def verbCodes(): return ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
def adjectiveCodes(): return ['JJ', 'JJR', 'JJS']
def adverbCodes(): return ['RB', 'RBR', 'RBS'] # should this include RP

# contains the 'can have' relation between chunk and pos
def isPosPartOf(pos, chunk):
    wordsOfChunk = {'NP':['DT'] + adverbCodes() + adjectiveCodes() + nounCodes() + ['PRP'],
        'PP':['TO', 'IN'],
        'VP':adverbCodes() + ['MD'] + verbCodes(),
        'ADVP':adverbCodes(),
        'ADJP':['CC'] + adverbCodes() + adjectiveCodes(),
        'SBAR':['IN'],
        'PRT':['RP'],
        'INTJ':['UH']}
    return True if chunk in wordsOfChunk and pos in wordsOfChunk[chunk] else False