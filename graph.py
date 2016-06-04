from pattern.graph import Graph
import sqlite3 as sql

graph = Graph()

connection = sql.connect('emma.db')
cursor = connection.cursor()

with connection:
    cursor.execute('SELECT * FROM associationmodel;')
    SQLReturn = cursor.fetchall()
for row in SQLReturn:
    graph.add_node(row[1])
    graph.add_node(row[3])
    
    if row[2] == "IS-A":
        graph.add_edge(row[1], row[3], weight=row[4], type=row[2], stroke=(1,0,0,1))
    if row[2] == "HAS-ABILITY-TO":
        graph.add_edge(row[1], row[3], weight=row[4], type=row[2], stroke=(0,1,0,1))
    if row[2] == "IS-PART-OF":
        graph.add_edge(row[1], row[3], weight=row[4], type=row[2], stroke=(0,0,1,1))
    if row[2] == "IS-RELATED-TO":
        graph.add_edge(row[1], row[3], weight=row[4], type=row[2], stroke=(1,0,1,1))
    
for n in sorted(graph.nodes, key=lambda n: n.weight):
    print '%.2f' % n.weight, n
    
graph.export('tail', directed=True, weighted=True)