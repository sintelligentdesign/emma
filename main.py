import random, ast

# load up the brain from reader. we'll link these later
brain = ast.literal_eval(open("testbrain.brn", "r").read())

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

print "OUTPUT: " + sentence
