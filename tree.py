import pattern.en

inputText = raw_input("Message: ")
pattern.en.pprint(pattern.en.parse(inputText,relations=True,lemmata=True))