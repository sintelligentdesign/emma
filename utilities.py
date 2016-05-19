import ast

#gets brain
brainfile = raw_input("File to scan: ")
brain = ast.literal_eval(open(brainfile, "r").read())

#finds largest freq number
maxFreq = 0
for key in brain:
    innerDict = brain[key]
    for value in innerDict.values():
        if value > maxFreq:
            maxFreq = value


#finds occurances of freq number
for count in range(1, maxFreq + 1):
    occurancesOfCount = 0
    for key in brain:
        innerDict = brain[key]
        for value in innerDict.values():
            if value == count:
                occurancesOfCount += 1
    if occurancesOfCount > 0:
        print 'Freq value ' + str(count) + ': found ' + str(occurancesOfCount) + ' time(s).'

#finds largest number of leafs on one stem
maxLeafs = 0
for value in brain.values():
    if len(value) > maxLeafs:
        maxLeafs = len(value)

#finds chance of stem having muliple leafs
for count in range(1, maxLeafs + 1):
    occurancesOfCount = 0
    for value in brain.values():
        if len(value) == count:
            occurancesOfCount += 1
    if occurancesOfCount:
        print 'Stems had ' + str(count) + " leafs " + str(occurancesOfCount) + ' time(s).'
