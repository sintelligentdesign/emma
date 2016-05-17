import random
import ast

# load up the brain from reader. we'll link these later
brain = ""
brainfile = open("testbrain.brn", "r")
for line in brainfile:
    brain += line
brain = ast.literal_eval(brain)

speaklength = 20
sentence = "the wheels"
diesides = int

# create the sentence
while speaklength > 0:
#    word = random.choice(brain.keys())
#    sentence += word

#    diesides = word.values()
#    for count in range(0, len(diesides)):

    lastTwoWords = " ".join(sentence.split()[-2:])
    for key in brain:
        if key == lastTwoWords:
            totOccurances = 0
            nextWordsDict = brain[key]
            for word in nextWordsDict:
                totOccurances += nextWordsDict[word]

            selector = random.randrange(totOccurances) +1
            for word in nextWordsDict:
                selector -= nextWordsDict[word]
                if selector <= 0:
                    sentence += " " + word

#    sentence += " banana"

    speaklength -= 1

print "OUTPUT: " + sentence
