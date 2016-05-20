while 0 > 1:    # since i'm going to start using this file, i wanted to make sure nothing was executed
    #finds largest freq number
    maxFreq = 0
    for key in brain:
        innerDict = brain[key]
        for value in innerDict.values():
            if value > maxFreq:
                maxFreq = value


    #finds occurances of freq number
    for count in range(1, maxFreq + 1):
        occurancesOfCount = 0
        for key in brain:
            innerDict = brain[key]
            for value in innerDict.values():
                if value == count:
                    occurancesOfCount += 1
        if occurancesOfCount > 0:
            print 'Freq value ' + str(count) + ': found ' + str(occurancesOfCount) + ' time(s).'

    #finds largest number of leafs on one stem
    maxLeafs = 0
    for value in brain.values():
        if len(value) > maxLeafs:
            maxLeafs = len(value)

    #finds chance of stem having muliple leafs
    for count in range(1, maxLeafs + 1):
        occurancesOfCount = 0
        for value in brain.values():
            if len(value) == count:
                occurancesOfCount += 1
        if occurancesOfCount:
            print 'Stems had ' + str(count) + " leafs " + str(occurancesOfCount) + ' time(s).'

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