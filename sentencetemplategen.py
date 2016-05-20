# Sentence Template Generator.
# it generates sentence templates based on our parts of speech corpus.
# who'd've thunk it?
import random, ast

sentenceStructureModel = ast.literal_eval(open("sentencestructure.mdl", "r").read())    # load the generated sentence structure model

genLength = random.randrange(8, 25)
# todo: look for punctuation instead to tell us when to stop
sentenceTemplate = ""

sentenceTemplate += random.choice(sentenceStructureModel.keys())                        # choose the first two parts of speech to use as a stem
                                                                                        # these are chosen randomly

# Sentence Generation
while genLength > 0:
    hasNext = False                                         # keeps track of dead end status

    lastTwoPOS = " ".join(sentence.split()[-2:])            # retrieves the last two parts of speech we used
    if lastTwoPOS in sentenceStructureModel:
        totalOccurances = 0
        nextPOSDict = sentenceStructureModel[lastTwoPOS]
        for value in nextPOSDict.values():                  # finds total occurances for RNG limit
            totalOccurances += value

        selector = random.randrange(totalOccurances) +1     # RNG
        for key in nextPOSDict:                             # loops through next parts of speech, decrementing selector
            selector -= nextPOSDict[key]
            if selector <= 0:                               # choses following word when selector equals zero
                sentenceTemplate += " " + key

    else:                                                   # if we hit dead end, stick in a '%' so that we know that we hit a dead end and there should be more in the sentence model
        sentenceTemplate += "%"
        print "Sentence generation ended prematurely! (No leaves for stem %s)" % lastTwoPOS

    speaklength -= 1

if sentence.rfind('.') < 1:
    sentence += "."

sentence = str.join("", sentence.splitlines())
# todo: keep this as a list?

print "EMMA >> %s" % sentence