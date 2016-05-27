# Name:             Utilities
# Description       Miscellaneous functions that didn't fit anywhere else
# Section:          INPUT
# Writes/reads:
# Dependencies:
# Dependency of:    broca, conceptgen, emma

def personalpronountargetswap(sentence):
    # swap the targets of posessive words like you or mine so that Emma doesn't start going around calling other people Emma, etc.
    for count, word in enumerate(sentence):
        if word == "you":
            sentence[count] = "me"
        elif word == "me":
            sentence[count] = "you"

        elif word == "your":
            sentence[count] = "my"
        elif word == "my":
            sentence[count] = "your"

        elif word == "yours":
            sentence[count] = "mine"
        elif word == "mine":
           sentence[count] = "yours"
    return sentence

def consolidateduplicates(dupeList):
    # list object duplicate finder and remover function
    toRemove = []
    print "Consolidating duplicates in %s" % str(dupeList)
    for count in range(0, len(dupeList)):
        elem = dupeList[count]
        if elem.lower() in dupeList[count + 1:]:
            toRemove.append(elem)
    for dupe in toRemove:
        dupeList.remove(dupe)
    print "After consolidation: %s" % str(dupeList)
    return dupeList
    
def decodecapitalizationscore(score):
    # decodes the score object in nouninfo    
    score = score.split('/')    # decode the score code into its parts
    score = map(int, score)     # scores are stored as (lowercase/titlecase/uppercase), where each value is an int from 0 to 10
    return score
    
def encodecapitalizationscore(splitScore):
    # packages split score (a list of integers) into the format stored in nouninfo
    for count, score in enumerate(splitScore):  # add leading zeros to each int
        score = str(score).zfill(2)
        splitScore[count] = score
    score = '/'.join(splitScore)                # package the list into a string
    return score