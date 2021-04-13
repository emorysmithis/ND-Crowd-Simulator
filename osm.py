#!/usr/bin/env python
import osmnx as ox
import matplotlib.pyplot as plt


# Get ND graph
place_name = 'Notre Dame, Indiana, United States'
graph = ox.graph_from_place(place_name)
#fig, ax = ox.plot_graph(graph)
#plt.tight_layout()

# Adding buildings
area = ox.geocode_to_gdf(place_name)
buildings = ox.geometries_from_place(place_name, tags={'building':True})
nodes, edges = ox.graph_to_gdfs(graph)
'''
fig, ax = plt.subplots()
area.plot(ax=ax, facecolor='black')
nodes.plot(ax=ax, facecolor='red', markersize=0.2, zorder=3)
edges.plot(ax=ax, linewidth=1, edgecolor='#BC8F8F')
buildings.plot(ax=ax, facecolor='khaki', alpha=0.7)
plt.tight_layout()
'''

# Path for library -> bookstore
# try to use building names instead of coordinates 
orig_node = ox.get_nearest_node(graph, (41.70279, -86.23473)) # library 
target_node = ox.get_nearest_node(graph, (41.69683, -86.24036)) # bookstore
target_node = ox.get_nearest_node(graph, (41.6972833, -86.2345329)) # ONeill Hall
node_list = ox.distance.shortest_path(graph, orig_node, target_node)
nodes_path = nodes.loc[node_list]
#nodes_path

# Plot the nodes
fig, ax = plt.subplots()
area.plot(ax=ax, facecolor='black')
buildings.plot(ax=ax, facecolor='khaki', alpha=0.7)
edges.plot(ax=ax, linewidth=1, edgecolor='#BC8F8F')
nodes_path.plot(ax=ax, markersize=0.4, facecolor='red', zorder=3)
plt.show() 
