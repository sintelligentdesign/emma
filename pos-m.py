# Parts of Speech Markov model generator
# note: model contents are wiped on each run
# todo: fix that
import nltk, re, pprint

sentencepos = []
stem = {}
leaf = {}

target = "partsofspeech.mdl"    # this isn't hard-coded just in case we want to reuse this code later

def getPartsOfSpeech(sentence):
    # get the parts of speech from the input
    sentence = nltk.sent_tokenize(sentence)                         # NLTK default sentence segmenter (todo: this should go in the main logic later)
    #sentence = [nltk.word_tokenize(sent) for sent in sentences]    # NLTK default word tokenizer (todo: this should go in the main logic later)
                                                                    # note: do we want to use the multi word expression tokenizer instead (to help with glue words)?
    sentence = nltk.word_tokenize(str(sentence).strip('[]'))      
    sentence = nltk.pos_tag(sentence)                               # NLTK default part-of-speech tagger
    print sentence
    
    # extract parts of speech as array from tuple
    for count in range (0, len(sentence)):
        sentencepos.append(sentence[count])
        print sentencepos

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
