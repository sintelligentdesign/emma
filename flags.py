# Debug mode
enableDebugMode = False

# Testing Strings
useTestingStrings = True
testingStringType = 'simple'
'''
testingStringsSimple = [
    u"The sky is blue.",
    u"Dogs are very fluffy!",
    u"I want to be your friend.",
    u"I love pickles!",
    u"The quick brown fox jumped over the lazy dog."
]
'''
testingStringsSimple = [
    u"Bees are yellow and black."
]

if testingStringType == 'simple':
    testingStrings = testingStringsSimple
elif testingStringType == 'fuzz':
    with open('utils/questions.txt', 'r') as file:
        testingStrings = [line.decode('utf-8', 'ignore').strip() for line in file.readlines()]