# Name:             Parts of Speech Markov model generator
# Description:      Takes input as parts of speech and adds them to a Markov model
# Section:          LEARNING
# Writes/reads:     emma.brn/sentencestructure.mdl
# Dependencies:     nltk, re, pprint, ast
# Dependency of:    emma
import nltk, re, pprint, ast

target = "emma.brn/sentencestructure.mdl"

def getPartsOfSpeech(sentence):
    # get the parts of speech from the input
    sentence = nltk.pos_tag(sentence)                             # NLTK default part-of-speech tagger

    tagSentence = []    # make "sentences" of tags from list of tuples
                        # the above is clearly a list, but we're calling it a sentence because as far as the markov muncher cares, it is one
                        # we could turn it into a string, but what's the point of doing that if we're gonna unpack it back into a list anyway?
    for count in range(0, len(sentence)):
        tup = sentence[count]
        tagSentence.append(tup[1])
    return tagSentence

def grok(input):
    POSArray = getPartsOfSpeech(input)

    # Overwrite prevention
    modelFile = open(target, "r")
    stem = {}                               # if partsofspeech.mdl is empty, stem is initialized and blank
    if modelFile != "":
        for line in modelFile:
            stem = ast.literal_eval(line)   # otherwise, stem is populated with the links from partsofspeech.mdl
    modelFile.close()
    
    leaf = {}

    for count in range(0, len(POSArray)):
        if count < len(POSArray) - 2:  # so we don't go out of bounds
            StemAsString = POSArray[count] + ' ' + POSArray[count + 1]          # take two parts of speech (the "stem")
            LeafAsString = POSArray[count + 2]                                  # also get one part of speech after the former two (the "leaf")

            if StemAsString in stem:                                            # check for duplicate stems

                leaf = stem[StemAsString]                                       # set value of leaf to CURRENT leaf

                if LeafAsString in leaf:                                        # if duplicate leaf, increment ranking
                    leaf[LeafAsString] += 1
                else:                                                           # otherwise, append new leaf to leaf list
                    leaf[LeafAsString] = 1

            else:
                leaf = {LeafAsString: 1}                                        # create dict with leaf and ranking if current stem isn't a dupe of another stem
                print "New sentence structure building block found (%s)! Adding..." % StemAsString

            stem[StemAsString] = leaf

    modelFile = open(target, "w")
    print >>modelFile, stem
    modelFile.close()