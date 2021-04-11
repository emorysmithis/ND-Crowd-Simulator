import osmnx as ox 
import matplotlib.pyplot as plt

place_name = 'Notre Dame, Indiana, United States'
graph = ox.graph_from_place(place_name)
fig, ax = ox.plot_graph(graph)
plot = plt.tight_layout() 
plt.show(plot)
