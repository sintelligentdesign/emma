# Parts of Speech Markov model generator
# note: model contents are wiped on each run
# todo: fix that
import nltk, re, pprint

stem = {}
leaf = {}

target = "partsofspeech.mdl"    # this isn't hard-coded just in case we want to reuse this code later

def getPartsOfSpeech(sentence):
    # get the parts of speech from the input
    sentences = nltk.sent_tokenize(document)                        # NLTK default sentence segmenter       todo: this should be in the main program
    sentences = nltk.word_tokenize(str(sentences).strip('[]\''))    # NLTK default word tokenizer           todo: this should be in the main program
    sentences = nltk.pos_tag(sentences)                             # NLTK default part-of-speech tagger
    print sentences
    
    # make "sentences" of tags from list of tuples
    tagsentence = []                                # this is clearly a list, but we're calling it a sentence because as far as the markov muncher cares, it is one
                                                    # we could turn it into a string, but what's the point of doing that if we're gonna unpack it back into a list anyway?
    for count in range(0, len(sentences)):
        tup = sentences[count]
        tansentence.append(tup[1])
    print "tag sentence: " + tagsentence
    return tagsentence

def grok(input):
    posarray = getPartsOfSpeech(input)

    for count in range(0, len(posarray)):
        if count < len(posarray) - 2:  # so we don't go out of bounds
            StemAsString = posarray[count] + ' ' + posarray[count + 1]          # take two parts of speech (the "stem")
            LeafAsString = posarray[count + 2]                                  # also get one part of speech after the former two (the "leaf")

            if StemAsString in stem:                                            # check for duplicate stems
                print "Duplicate stem detected: (" + StemAsString + "). Merging..."
                leaf = stem[StemAsString]                                       # set value of leaf to CURRENT leaf

                if LeafAsString in leaf:                                        # if duplicate leaf, increment ranking
                    leaf[LeafAsString] += 1
                else:                                                           # otherwise, append new leaf to leaf list
                    leaf[LeafAsString] = 1

            else:
                leaf = {LeafAsString: 1}                                        # create dict with leaf and ranking if current stem isn't a dupe of another stem

            stem[StemAsString] = leaf

    # todo: dump to brain.brn/"target"
    print "Parse complete. Dumping to" target
    modelfile = open(target, "w")
    print >>modelfile, stem
    modelfile.close()
    # todo: convert currentwords to json?
    # todo: let user choose files to read from and write to
