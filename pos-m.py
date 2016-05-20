# Parts of Speech Markov model generator
# note: model contents are wiped on each run
# todo: fix that: import contents of partsofspeech.mdl and use it while comparing in grok()
import nltk, re, pprint, ast

target = "partsofspeech.mdl"

def getPartsOfSpeech(sentence):
    # get the parts of speech from the input
    sentence = nltk.sent_tokenize(sentence)                       # NLTK default sentence segmenter       todo: this should be in the main program
    sentence = nltk.word_tokenize(str(sentence).strip('[]\''))    # NLTK default word tokenizer           todo: this should be in the main program
    sentence = nltk.pos_tag(sentence)                             # NLTK default part-of-speech tagger
    print sentence

    # make "sentences" of tags from list of tuples
    tagsentence = []
    # the above is clearly a list, but we're calling it a sentence because as far as the markov muncher cares, it is one
    # we could turn it into a string, but what's the point of doing that if we're gonna unpack it back into a list anyway?
    for count in range(0, len(sentence)):
        tup = sentence[count]
        tagsentence.append(tup[1])
    print "tag sentence: " + ' '.join(tagsentence)
    return tagsentence

def grok(input):
    posarray = getPartsOfSpeech(input)
    stem = ast.literal_eval(open(target, "r").read())                          #prevents overwrite
    leaf = {}

    for count in range(0, len(posarray)):
        if count < len(posarray) - 2:  # so we don't go out of bounds
            StemAsString = posarray[count] + ' ' + posarray[count + 1]          # take two parts of speech (the "stem")
            LeafAsString = posarray[count + 2]                                  # also get one part of speech after the former two (the "leaf")

            if StemAsString in stem:                                            # check for duplicate stems
                print "Duplicate stem detected: (%s). Merging..." % StemAsString

                leaf = stem[StemAsString]                                       # set value of leaf to CURRENT leaf

                if LeafAsString in leaf:                                        # if duplicate leaf, increment ranking
                    leaf[LeafAsString] += 1
                else:                                                           # otherwise, append new leaf to leaf list
                    leaf[LeafAsString] = 1

            else:
                leaf = {LeafAsString: 1}                                        # create dict with leaf and ranking if current stem isn't a dupe of another stem

            stem[StemAsString] = leaf

    print "Parse complete. Dumping to %s" % target
    modelfile = open(target, "w")
    print >>modelfile, stem
    modelfile.close()
    # todo: convert to json?

while 1>0:
    grok(raw_input("INPUT: "))
