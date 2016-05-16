import random
import ast

# load up the brain from reader. we'll link these later
brain = ""
brainfile = open("testbrain.brn", "r")
for line in brainfile:
    brain += line
brain = ast.literal_eval(brain)
    
speaklength = 20
sentence = ""
diesides = int

# create the sentence
while speaklength > 0:
    word = random.choice(brain.keys())
    sentence += word
    
    diesides = word.values()
    for count in range(0, len(diesides)):
        
    
    speaklength -= 1