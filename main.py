import random
import ast

# load up the brain from reader. we'll link these later
brain = ""
brainfile = open("testbrain.brn", "r")
for line in brainfile:
    brain += line
brain = ast.literal_eval(brain)

speaklength = randrange(8, 25)
sentence = "the wheels"         #basic seed
diesides = int

# create the sentence
while speaklength > 0:
#    word = random.choice(brain.keys())
#    sentence += word

#    diesides = word.values()
#    for count in range(0, len(diesides)):

    lastTwoWords = " ".join(sentence.split()[-2:])                              #gets last two words in sentence
    for key in brain:                                                           #finds last two words
        if key == lastTwoWords:                                                 #finds following words in brain
            totOccurances = 0
            nextWordsDict = brain[key]
            for word in nextWordsDict:                                          #finds total Occurances for RNG limit
                totOccurances += nextWordsDict[word]

            selector = random.randrange(totOccurances) +1                       #RNG
            for word in nextWordsDict:                                          #loops through decrementing selector
                selector -= nextWordsDict[word]
                if selector <= 0:                                               #choses following word when selector equals zero
                    sentence += " " + word

    speaklength -= 1
    
sentence += "."

print "OUTPUT: " + sentence
