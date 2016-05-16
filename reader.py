wordarray = []
currentwords = {}
nextword = {}

with open ("testbrain.txt", "r") as corpus:
    for line in corpus:
        # todo: remove and take note of punctuation for punctuation model
        # todo: remove unicode characters and newlines?
        wordarray = wordarray + line.split(' ')

for count in range(0, len(wordarray)):
    dupedetected = 0    # bit for carrying duplication detected message
    if count < len(wordarray) - 2:  # so we don't go out of bounds
        CurrentWordsAsString = wordarray[count] + ' ' + wordarray[count + 1]    # take two words
        NextWordAsString = wordarray[count + 2]                                 # also get the word after the two words
        
        # todo: figure out dups and ranking
        for count in range(0, len(currentwords)):                               # check through everything we've done so far to see if we have duplicate currentwords values
            if CurrentWordsAsString == currentwords.keys()[count]:              # check CurrentWordsAsString against each established previous first two word pair
                print "Duplicate currentwords detected: " + CurrentWordsAsString + ". Merging..."
                dupedetected = 1
                        
                nextword = currentwords.values()[count]                         # set value of nextword to CURRENT nextword
                
                for count in range(0, len(nextword)):                           # if we've already set nextword, increment its score
                    if nextword.keys()[count] == NextWordAsString:
                        nextword[NextWordAsString] += 1
                    else:                                                       # otherwise, append new next word to nextword list
                        nextword[NextWordAsString] = 1                          
                
        if dupedetected == 0:
            nextword = {NextWordAsString: 1}                                    # create dict with next word and ranking if currentwords isn't a dupe of another key
        
        currentwords[CurrentWordsAsString] = nextword  
        
print "Parse complete. Dumping to testbrain.brn"
brainfile = open("testbrain.brn", "w")
print >>brainfile, currentwords
brainfile.close()
# todo: convert currentwords to json
# todo: let user choose files to read from and write to
# todo: replace currentwords and nextword with stem and leaf?