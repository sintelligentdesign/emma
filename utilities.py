# Name:             Utilities
# Description       Miscellaneous functions that didn't fit anywhere else
# Section:          INPUT
# Writes/reads:
# Dependencies:
# Dependency of:    broca, conceptgen, emma

def personalpronountargetswap(word):
    # swap the targets of posessive words like you or mine so that Emma doesn't start going around calling other people Emma, etc.
    if word == "you":
        word == "me"
    elif word == "me":
        word == "you"

    elif word == "your":
        word == "my"
    elif word == "my":
        word == "your"

    elif word == "yours":
        word == "mine"
    elif word == "mine":
        word == "yours"

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
