# todo: add commands for user to quit command line and delete contents of .brn file?
wordarray = []
stem = {}
leaf = {}

while 1 > 0:
    userinput = raw_input('INPUT >> ')
    # todo: remove and take note of punctuation for punctuation model
    wordarray = userinput.split(' ')

    for count in range(0, len(wordarray)):
        if count < len(wordarray) - 2:  # so we don't go out of bounds
            StemAsString = wordarray[count] + ' ' + wordarray[count + 1]        # take two words (the "stem")
            LeafAsString = wordarray[count + 2]                                 # also get the word after the two words (the "leaf")

            # todo: figure out dups and ranking
            if StemAsString in stem:                                       # check for duplicate stems
                print "Duplicate stem detected: (" + StemAsString + "). Merging..."

                leaf = stem[StemAsString]                                 # set value of leaf to CURRENT leaf

                if LeafAsString in leaf:                                # if duplicate leaf, increment score
                    leaf[LeafAsString] += 1
                else:                                                   # otherwise, append new leaf to leaf list
                    leaf[LeafAsString] = 1

            else:
                leaf = {LeafAsString: 1}                                        # create dict with leaf and ranking if current stem isn't a dupe of another stem

            stem[StemAsString] = leaf

    print "Parse complete. Dumping to linetestbrain.brn"
    brainfile = open("linetestbrain.brn", "w")
    print >>brainfile, stem
    brainfile.close()
    # todo: convert currentwords to json?
    # todo: let user choose files to read from and write to
