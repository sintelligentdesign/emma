wordarray = []
stem = {}
leaf = {}

readfrom = raw_input('File to read from: ')
writeto = raw_input('File to write to: ')

with open (readfrom, "r") as corpus:
    for line in corpus:
        # todo: remove and take note of punctuation for punctuation model
        wordarray = wordarray + line.split(' ')

for count in range(0, len(wordarray)):
    if count < len(wordarray) - 2:  # so we don't go out of bounds
        StemAsString = wordarray[count] + ' ' + wordarray[count + 1]        # take two words (the "stem")
        LeafAsString = wordarray[count + 2]                                 # also get the word after the two words (the "leaf")

        # todo: figure out dups and ranking
        if StemAsString in stem:                                          #check for duplicate stems
            print "Duplicate stem detected: (" + StemAsString + "). Merging..."

            leaf = stem[StemAsString]                                # set value of leaf to CURRENT leaf

            if LeafAsString in leaf:                                  # if we've already set this as a leaf, increment its score
                leaf[LeafAsString] += 1
            else:                                                     # otherwise, append new leaf to leaf list
                leaf[LeafAsString] = 1

        else:
            leaf = {LeafAsString: 1}                                   # create dict with leaf and ranking if current stem isn't a dupe of another stem

        stem[StemAsString] = leaf                                      # now that leaf is built, put it in stem

print "Parse complete. Dumping to " + writeto
brainfile = open(writeto, "w")
print >>brainfile, stem
brainfile.close()
