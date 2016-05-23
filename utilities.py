# Name:             Utilities
# Description       Miscellaneous functions that didn't fit anywhere else
# Section:          INPUT
# Writes/reads:
# Dependencies:
# Dependency of:

def personalpronountargetswap(word):
    # swap the targets of posessive words like you or mine so that Emma doesn't start going around calling other people Emma, etc.
    if word == "you":
        word == "me"
    elif word == "me":
        word == "you"
        
    elif word == "your":
        word == "my"
    elif word == "my":
        word == "your"
        
    elif word == "yours":
        word == "mine"
    elif word == "mine":
        word == "yours"