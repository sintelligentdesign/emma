# Name:             Graph-Related Functions
# Description:      General stuff that requires pattern.graph
# Section:          REPLY
# Writes/reads:     emma.brn/conceptgraph.db
# Dependencies:     pattern.graph, sqlite3
# Dependency of:    
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

def find_related_words(word, association):
    adjacencyList = pattern.graph.adjacency(graph, directed=True, stochastic=True)
    tier1 = adjacencyList[word]
    print tier1
    tier2 = []
    for node in tier1:
        tier2.append(adjacencyList[node])
    print tier2

with connection:
    cursor.execute('SELECT * FROM associationmodel;')
    SQLReturn = cursor.fetchall()
for row in SQLReturn:
    create_edge(row[1], row[3], row[2], row[4])
    
graph.export('tail', directed=True, weighted=True)
find_related_words('cat', 0)