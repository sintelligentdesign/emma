     .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.
    d88' `88b `888P"Y88bP"Y88b  `888P"Y88bP"Y88b  `P  )88b
    888ooo888  888   888   888   888   888   888   .oP"888
    888    .,  888   888   888   888   888   888  d8(  888
    `Y8bod8P' o888o o888o o888o o888o o888o o888o `Y888""8o

       ·~-.¸¸,.-~*¯¨*·~-.¸,.-~*¯¨*·~-.¸¸,.-~*¯¨*·~-.¸¸,.

             EXPANDING MODEL of MAPPED ASSOCIATIONS


       Written by Ellie Cochran & Alexander Howard, with
                 contributions by Omri Barak.

Emma is a computer program that generates rough concepts of associations by reading input. She uses these associations, in conjunction with learned sentence structure patterns, to generate a reply (consequently, Emma is *not* a run-of-the-mill Markov bot. She's much more interesting than that~). She is a Summer project created by Digital Media student, programmer, & computer artist Ellie Cochran, and Computer Science & Mathematics student Alexander Howard, with some contributions by Omri Barak.

###Progress towards completion
     [0%]▨▨▨▨▨▨▨▨[25%]▢▢▢▢▢▢▢[50%]▢▢▢▢▢▢▢[75%]▢▢▢▢▢▢▢[100%]

##How Emma Works
(to-do)

#Talk to Emma
Emma isn't online yet, but when she is we'll hook up a conversation interface using Tumblr "asks" as a frontend. You will be able to talk to Emma at [emmacanlearn.tumblr.com](http://emmacanlearn.tumblr.com).

##To-Do
The following features are on our list of things to implement once Emma's core feature set is complete:
* Create a paragraph model that is trained on the sentences in the input to help Emma decide when to end paragraphs and what kinds of sentences should follow other sentences.
  * Should the number of sentenes in the input affect the number of sentences attempted in the output?
* Write some way of visualizing the Concept Graph. It'd be so cool to see
  * Association strength could be represented using line opacity
  * Lines could have arrows indicating directionality
* We need to find a special way to handle questions
  * There's not a lot of new information that can be gleaned from questions
  * Questions, by their nature, are information holes requesting to be filled
  * We could generate an "answer" sentence type, or a question could prompt Emma to list things she knows about nouns in the question based on the strongest associations (for example, an input of "What are cats?" would prompt a reply of "Cats are furry, soft, gentile, and sweet. They explore, meow, purr, and sleep")
  
##Contact the Developers
Ellie and Alex are on social media! Ask us about Emma!
Ellie Cochran is [@sharkthemepark](http://sharkthemepark.tumblr.com) on Tumblr and Twitter.
Alexander Howard is [@ale303sh](http://www.twitter.com/ale303sh) on Twitter.
