# Name:             Utilities
# Description       Miscellaneous functions that didn't fit anywhere else
# Section:          INPUT
# Writes/reads:
# Dependencies:
# Dependency of:    broca, conceptgen, emma

def personalpronountargetswap(sentence):
    # swap the targets of posessive words like you or mine so that Emma doesn't start going around calling other people Emma, etc.
    for count, word in enumerate(sentence):
        print word
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

# list object duplicate finder and remover function
def consolidateduplicates(dupeList):
    toRemove = []
    print "Before consolidation: %s" % str(dupeList)
    for count in range(0, len(dupeList)):
        elem = dupeList[count]
        if elem in dupeList[count + 1:]:
            toRemove.append(elem)
    for dupe in toRemove:
        dupeList.remove(dupe)
    print "After consolidation: %s" % str(dupeList)
    return dupeList