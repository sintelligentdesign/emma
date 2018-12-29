     .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.
    d88' `88b `888P"Y88bP"Y88b  `888P"Y88bP"Y88b  `P  )88b
    888ooo888  888   888   888   888   888   888   .oP"888
    888    .,  888   888   888   888   888   888  d8(  888
    `Y8bod8P' o888o o888o o888o o888o o888o o888o `Y888""8o

            ELECTRONIC MODEL of MAPPED ASSOCIATIONS

          Written by Ellie Cochran & Alexander Howard

Emma is a computer program that generates rough concepts of associations by reading input. She uses these associations to generate a reply (consequently, Emma is *not* a run-of-the-mill Markov bot. She's much more interesting than that~). She was created by Digital Media student, programmer, & computer artist Ellie Cochran with help from Computer Science & Mathematics student Alexander Howard.

# Talk to Emma
You can talk to Emma using Tumblr Asks at [@emma@botsin.space](https://botsin.space/@emma).

## How Does Emma Work?
1. Emma reads a message from Mastodon
  - The message is first prepared to be read, which involves screening for banned words or vulgar language, as well as expanding common abbreviations and adding punctuation if none exists
  - The positive or negative sentiment of the message is recorded and used along with other sentiments from other messages to calculate Emma's mood
  - The message Emma has chosen to respond to is parsed using pattern.en
    - This gives us all kinds of information about the language used, including lemata, chunks, chunk relations, and parts of speech
  - We look through the new metadata-tagged sentences to fix up any remaining things that could hinder Emma's understanding, such as evaluating pronouns and posessive references
  - Emma reads through the sentences and records any new words she finds, along with their parts of speech and a (currently unused) affinity score
  - Emma uses a pattern matching strategy to find key phrase structures in the message that indicate a relationship between two objects, and records the objects and their relationship
    - This is what makes up Emma's Association Model
    - Current association types are IS-A, HAS-PROPERTY, HAS-ABILITY-TO, HAS, and HAS-OBJECT
      - As a side note, HAS-OBJECT refers not to a noun that another noun has in its posession, but to an object of a sentence that is valid for a noun to use
    - Associations are also weighted
2. Emma replies to the message and posts the response to Mastodon
  - Emma looks for important words in the message to figure out what it's about
  - Emma decides the number and types of sentences to generate
    - This is based on the types of associations that exist for a given object. For example, if plenty of IS-A associations exist, a DECLARATIVE sentence could be generated. If no or few associations exist, an INTERROGATIVE sentence could be generated.
    - This is influenced by Emma's mood
  - Emma creates rough outlines of the sentence, which include placeholders for articles, conjunctions, punctuation, and words that can change based on noun plurality
  - The placeholders are conjugated based on their surrounding words, and capitalization and punctuation are added
  - The reply is posted to Mastodon

## Contact the Developers
Ellie and Alex are on social media! Ask us about Emma!
Ellie is [@deersyrup@yiff.life](http://yiff.life/@deersyrup) on Mastodon, and Alex is [@ale303sh](http://www.twitter.com/ale303sh) on Twitter.

## Special Thanks
 * Omri Barak
 * Alexander Lozada
