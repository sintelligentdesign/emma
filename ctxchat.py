import emma

name = raw_input('What is your name? ')

while True:
    message = raw_input('%s >> ' % name)
    emma.input(message.encode('utf-8'), name.encode('utf-8'))