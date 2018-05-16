# Debug mode
enableDebugMode = True

# Testing Strings
useTestingStrings = True
testingStringType = 'simple'

testingStringsSimple = [
    # u"Jane is smart. Her eyes are blue.",
    # u"You look so good! I love your beans. They are great!",
    # u"The sky is blue.",
    u"Dogs are very fluffy!",
    u"Dogs are cute.",
    u"That dog is adorable!"
    # u"I want to be your friend.",
    # u"I love pickles!",
    # u"The quick brown fox jumped over the lazy dog."
]
'''
testingStringsSimple = [
    u"What is the color of the sky?"
]
'''
if testingStringType == 'simple':
    testingStrings = testingStringsSimple
elif testingStringType == 'fuzz':
    with open('utils/questions.txt', 'r') as file:
        testingStrings = [line.decode('utf-8', 'ignore').strip() for line in file.readlines()]