# Name:             Configuration File
# Description:      Emma's "control panel"
# Section:          
# Writes/reads:     
# Dependencies:     
# Dependency of:    emma, conceptgen

### Define what parts of speech signify nouns, verbs, and adjectives
def nounCodes(): return ['NN', 'NNS', 'NNP', 'NNPS']
def verbCodes(): return ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
def adjectiveCodes(): return ['JJ', 'JJR', 'JJS']