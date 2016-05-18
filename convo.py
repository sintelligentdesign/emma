import random, ast

wordarray = []
stem = ast.literal_eval(open("convo.brn", "r").read())                          #prevents overwrite of .brn file
leaf = {}

while 1 > 0:
    userinput = raw_input('YOU >> ')
    wordarray = userinput.split(' ')

    for count in range(0, len(wordarray)):
        if count < len(wordarray) - 2:  # so we don't go out of bounds
            StemAsString = wordarray[count] + ' ' + wordarray[count + 1]        # take two words (the "stem")
            LeafAsString = wordarray[count + 2]                                 # also get the word after the two words (the "leaf")

            if StemAsString in stem:                                       # check for duplicate stems
                leaf = stem[StemAsString]                                 # set value of leaf to CURRENT leaf
                if LeafAsString in leaf:                                # if duplicate leaf, increment score
                    leaf[LeafAsString] += 1
                else:                                                   # otherwise, append new leaf to leaf list
                    leaf[LeafAsString] = 1
            else:
                leaf = {LeafAsString: 1}                                        # create dict with leaf and ranking if current stem isn't a dupe of another stem

            stem[StemAsString] = leaf

    #write to brain.
    brainfile = open("convo.brn", "w")
    print >>brainfile, stem
    brainfile.close()

    ##RESPONSE STARTS HERE##

    # load up the brain from reader
    brain = ast.literal_eval(open("convo.brn", "r").read())

    speaklength = random.randrange(8, 25)
    sentence = ""

    #choose first two words
    sentence += random.choice(brain.keys())
    #sets lives
    lives = 2

    # create the sentence
    while speaklength > 0 and lives > 0:
        hasNext = False  #keeps track of dead end status

        lastTwoWords = " ".join(sentence.split()[-2:])                              #gets last two words in sentence
        if lastTwoWords in brain:
            totOccurances = 0
            nextWordsDict = brain[lastTwoWords]
            for value in nextWordsDict.values():                                          #finds total Occurances for RNG limit
                totOccurances += value

            selector = random.randrange(totOccurances) +1                       #RNG
            for key in nextWordsDict:                                          #loops through next words, decrementing selector
                selector -= nextWordsDict[key]
                if selector <= 0:                                               #choses following word when selector equals zero
                    sentence += " " + key

        else:            #if dead end, adds new stem, decrements lives
            sentence += " " + random.choice(brain.keys())
            lives -= 1

        speaklength -= 1

    if sentence.rfind('.') < 1:
        sentence += "."

    sentence = str.join("", sentence.splitlines())

    print "MBOT: " + sentence
