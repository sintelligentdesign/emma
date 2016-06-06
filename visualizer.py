# Name:             Concept Graph Visualizer
# Description:      Tools for building a graphic representation of Emma's concept graph
# Section:          REPLY
import pattern.graph
import sqlite3 as sql

connection = sql.connect('emma.db')
cursor = connection.cursor()

graph = pattern.graph.Graph()

def create_edge(node1, node2, association, weight):
    graph.add_node(node1)
    graph.add_node(node2)
    
    if association == "IS-A":
        graph.add_edge(node1, node2, weight=weight, type=association, stroke=(1,0,0,weight))
    elif association == "IS-PART-OF":
        graph.add_edge(node1, node2, weight=weight, type=association, stroke=(0,1,0,weight))
    elif association == "IS-PROPERTY-OF":
        graph.add_edge(node1, node2, weight=weight, type=association, stroke=(0,0,1,weight))
    elif association == "IS-RELATED-TO":
        graph.add_edge(node1, node2, weight=weight, type=association, stroke=(1,0,1,weight))
    elif association == "IS-EFFECT-OF":
        graph.add_edge(node1, node2, weight=weight, type=association, stroke=(0,1,1,weight))
    elif association == "HAS-ABILITY-TO":
        graph.add_edge(node1, node2, weight=weight, type=association, stroke=(0,0,0,weight))
    
# Determine important nodes
def find_important_words():
    for n in sorted(graph.nodes, key=lambda n: n.weight):
        print '%.2f' % n.weight, n

with connection:
    cursor.execute('SELECT * FROM associationmodel;')
    SQLReturn = cursor.fetchall()
for row in SQLReturn:
    create_edge(row[1], row[3], row[2], row[4])
    
graph.export('emma', directed=True, weighted=True)