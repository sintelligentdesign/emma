# Name:             Association Trainer
# Description:      Finds and adds associations to Emma's association model
# Section:          LEARNING
import numpy as np
import re

import sqlite3 as sqlite3
from colorama import init, Fore
init(autoreset = True)

import utilities

connection = sql.connect('emma.db')
cursor = connection.cursor()