import emma
import settings

settings.load_settings()

name = raw_input('What is your name? ')

while True:
    message = raw_input('You >> ')
    emma.input(message, name)