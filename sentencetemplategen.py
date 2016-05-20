# Sentence Template Generator.
# it generates sentence templates based on our parts of speech corpus.
# who'd've thunk it?
import random, ast

sentenceStructureModel = ast.literal_eval(open("sentencestructure.mdl", "r").read())    # load the generated sentence structure model

sentenceTemplate = ""

sentenceTemplate += random.choice(sentenceStructureModel.keys())                        # choose a stem at random from our sentence building block model

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
                if key == "." or "?" or "!":
                    sentenceTemplate += key                 # if the next key is punctuation, end the sentence
                else:
                    sentenceTemplate += " " + key           # otherwise, append the part of speech

    else:                                                   # if we hit dead end, stick in a '%' so that we know that we hit a dead end and there should be more in the sentence model
        sentenceTemplate += "%"
        print "Sentence generation ended prematurely! (No leaves for stem %s)" % lastTwoPOS

sentence = str.join("", sentenceTemplate.splitlines())
# todo: keep this as a list?

print "EMMA >> %s" % sentence