import emma

name = raw_input('What is your name? ')

while True:
    message = raw_input('You >> ')
    emma.input(message, name)