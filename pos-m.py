# Parts of Speech Markov model generator
# note: model contents are wiped on each run
# todo: fix that
import nltk, re, pprint

wordarray = []
stem = {}
leaf = {}

target = "partsofspeech.mdl"

def getPartsOfSpeech(document):
    # get the parts of speech from the input
    sentences = nltk.sent_tokenize(document)                        # NLTK default sentence segmenter (todo: this should go in the main logic later.)
    print sentences
    sentences = [nltk.word_tokenize(sent) for sent in sentences]    # NLTK default word tokenizer
    print sentences
    sentences = [nltk.pos_tag(sent) for sent in sentences]          # NLTK default part-of-speech 
    print sentences
    
    # extract parts of speech as array from tuple
    # (TODO)

def grok(input)
PartsOfSpeechAsArray = getPartsOfSpeech(input)
userinput = raw_input('INPUT >> ')
wordarray = userinput.split(' ')

for count in range(0, len(wordarray)):
    if count < len(wordarray) - 2:  # so we don't go out of bounds
        StemAsString = wordarray[count] + ' ' + wordarray[count + 1]        # take two parts of speech (the "stem")
        LeafAsString = wordarray[count + 2]                                 # also get one part of speech after the former two (the "leaf")

        # todo: figure out dupes and ranking
        if StemAsString in stem:                                            # check for duplicate stems
            print "Duplicate stem detected: (" + StemAsString + "). Merging..."
            leaf = stem[StemAsString]                                       # set value of leaf to CURRENT leaf

            if LeafAsString in leaf:                                        # if duplicate leaf, increment score
                leaf[LeafAsString] += 1
            else:                                                           # otherwise, append new leaf to leaf list
                leaf[LeafAsString] = 1

        else:
            leaf = {LeafAsString: 1}                                        # create dict with leaf and ranking if current stem isn't a dupe of another stem

        stem[StemAsString] = leaf

print "Parse complete. Dumping to " target
brainfile = open(target, "w")
print >>brainfile, stem
brainfile.close()
# todo: convert currentwords to json?
# todo: let user choose files to read from and write to
