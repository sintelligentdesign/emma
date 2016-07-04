# Name:             Concept Graph Visualizer
# Description:      Tools for building a graphic representation of Emma's concept graph
# Section:          REPLY
import pattern.graph
import sqlite3 as sql
from config import files

connection = sql.connect(files['dbPath'])
cursor = connection.cursor()

graph = pattern.graph.Graph()

def create_edge(node1, node2, association, weight):
    graph.add_node(node1)
    graph.add_node(node2)
    
    if association == "IS-A":
        graph.add_edge(node1, node2, weight=weight, type=association, stroke=(1,0,0,weight))
    elif association == "IS-PART-OF":
        graph.add_edge(node1, node2, weight=weight, type=association, stroke=(0,1,0,weight))
    elif association == "HAS-PROPERTY":
        graph.add_edge(node1, node2, weight=weight, type=association, stroke=(0,0,1,weight))
    elif association == "HAS-ABILITY-TO":
        graph.add_edge(node1, node2, weight=weight, type=association, stroke=(1,0,1,weight))
    elif association == "IS-RELATED-TO":
        graph.add_edge(node1, node2, weight=weight, type=association, stroke=(0,1,1,weight))
    elif association == "HAS-OBJECT":
        graph.add_edge(node1, node2, weight=weight, type=association, stroke=(0,0,0,weight))

with connection:
    cursor.execute('SELECT * FROM associationmodel WHERE weight > 0.15;')
    SQLReturn = cursor.fetchall()
for row in SQLReturn:
    create_edge(row[0], row[2], row[1], row[3])
    
print "Emma >> Please enter the name of a directory where I can dump the visualization of my association model"
exportFolder = raw_input('Directory name: ./').replace("/", "")
graph.export(exportFolder, directed=True, weighted=True)
print "Graph exported under ./%s/" % exportFolder