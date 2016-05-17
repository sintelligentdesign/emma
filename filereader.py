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
    dupedetected = 0    # bit for carrying duplication detected message
    if count < len(wordarray) - 2:  # so we don't go out of bounds
        StemAsString = wordarray[count] + ' ' + wordarray[count + 1]        # take two words (the "stem")
        LeafAsString = wordarray[count + 2]                                 # also get the word after the two words (the "leaf")
        
        # todo: figure out dups and ranking
        for count in range(0, len(stem)):                                   # check through everything we've done so far to see if we have duplicate stem values
            if StemAsString == stem.keys()[count]:                          # check StemAsString against each established previous first two word pair
                print "Duplicate stem detected: (" + StemAsString + "). Merging..."
                dupedetected = 1
                        
                leaf = stem.values()[count]                                 # set value of leaf to CURRENT leaf
                
                for count in range(0, len(leaf)):                           # if we've already set this as a leaf, increment its score
                    if leaf.keys()[count] == LeafAsString:
                        leaf[LeafAsString] += 1
                    else:                                                   # otherwise, append new leaf to leaf list
                        leaf[LeafAsString] = 1                          
                
        if dupedetected == 0:
            leaf = {LeafAsString: 1}                                        # create dict with leaf and ranking if current stem isn't a dupe of another stem
        
        stem[StemAsString] = leaf
        
print "Parse complete. Dumping to testbrain.brn"
brainfile = open(writeto, "w")
print >>brainfile, stem
brainfile.close()