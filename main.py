import random
import ast

import linereader

brain = ""

while 1>0:
    # load brain
    brainfile = open("linetestbrain.brn", "r")
    for line in brainfile:
        brain += line
    brain = ast.literal_eval(brain)
    
    # prompt user for input 
    linereader.input()
    
    # REPLY LOGIC STARTS HERE
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
        for key in brain:                                                           #finds last two words
            if key == lastTwoWords:                                                 #finds following words in brain
                hasNext = True  #not dead end
                totOccurances = 0
                nextWordsDict = brain[key]
                for word in nextWordsDict:                                          #finds total Occurances for RNG limit
                    totOccurances += nextWordsDict[word]

                selector = random.randrange(totOccurances) +1                       #RNG
                for word in nextWordsDict:                                          #loops through next words, decrementing selector
                    selector -= nextWordsDict[word]
                    if selector <= 0:                                               #choses following word when selector equals zero
                        sentence += " " + word

        if hasNext == False:            #if dead end, adds new stem, decrements lives
            sentence += " " + random.choice(brain.keys())
            lives -= 1
            
        speaklength -= 1

    if sentence.rfind('.') < 1:
        sentence += "."

    sentence = str.join("", sentence.splitlines())
    print "HER: " + sentence