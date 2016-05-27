# Name:             Sentence template generator
# Description:      Generates sentence templates from our Markov model of parts of speech
# Section:          REPLY
# Writes/reads:     emma.brn/sentencestructure.mdl
# Dependencies:     random, ast
# Dependency of:    emma
import random, ast

# Sentence Generation
def generate():
    sentenceStructureModel = ast.literal_eval(open("emma.brn/sentencestructure.mdl", "r").read())    # load the generated sentence structure model
    sentenceTemplate = ""
    if not sentenceStructureModel == {}:
        sentenceTemplate += random.choice(sentenceStructureModel.keys())    # choose a stem at random from our sentence building block model

        while not (sentenceTemplate[-1] in ['.', '!', '?', '%']):
            lastTwoPOS = " ".join(sentenceTemplate.split()[-2:])            # retrieves the last two parts of speech we used

            if lastTwoPOS in sentenceStructureModel:                        # if the last two parts of speech constitute a valid stem...
                totalOccurances = 0                                         # find occurances of leaves to tell RNG how many numbers to choose from
                nextPOSDict = sentenceStructureModel[lastTwoPOS]
                for value in nextPOSDict.values():
                    totalOccurances += value
            else:                                                           # if the last two parts of speech aren't a valid stem, print an error character at the end of the sentence to let us know that there should be more words
                sentenceTemplate += " %"
                print "Sentence generation ended prematurely! (No leaves for stem %s)" % lastTwoPOS

            selector = random.randrange(totalOccurances) + 1                # RNG
            wordAdded = False

            for key in nextPOSDict:                                         # loop through leaves, decrementing selector, to choose the next leaf to follow
                selector -= nextPOSDict[key]
                if selector <= 0 and not wordAdded:                           # if the selector reaches zero, choose the next stem
                    wordAdded = True                                         # prevents repeat adding of words
                    if key in ['.', '!', '?']:                              # if the next leaf is punctuation, end the sentence
                        sentenceTemplate += key
                    else:
                        sentenceTemplate += " " + key                       # otherwise, append our next part of speech and loop back to line 19

    return sentenceTemplate

print generate()
