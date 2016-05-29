# Name:             Sentence Layout Generator
# Description:      Generates sentence layout templates from our Markov model of sentence chunks
# Section:          REPLY
# Writes/reads:     
# Dependencies:     random, ast, sqlite3
# Dependency of:    
import random
import ast

import sqlite3 as sql

connection = sql.connect('brain.db')
cursor = connection.cursor()

def generate():
    sentenceTemplate = ""
    
    with connection:
        cursor.execute('SELECT * FROM sentencestructuremodel')
        SQLReturn = cursor.fetchall()