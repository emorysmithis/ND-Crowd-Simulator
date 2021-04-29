#!/usr/bin/env python3

import sys
import osmnx as ox
import matplotlib.pyplot as plt
import geopandas

def setup_osm(place_name):
    graph = ox.graph_from_place(place_name)
    buildings = ox.geometries_from_place(place_name, tags={'building':True})
    area = ox.geocode_to_gdf(place_name)
    nodes, edges = ox.graph_to_gdfs(graph)
    return graph, buildings, area, edges

def load_output(output_file):
    should_read = False             # boolean for whether or not line is edge info
    edges_dict = {}

    with open(output_file, 'r') as f:
        for line in f:
            
            # Data separator
            if '--------' in line:
                should_read = not should_read
                continue

            # Update edges_dict
            if should_read:
                u_v, value = line.strip().split()
                edges_dict[u_v] = int(value)
    
    print(edges_dict)        
    return edges_dict

if __name__ == '__main__':
    
    # Get graph object
    graph, buildings, area, edges = setup_osm('Notre Dame, Indiana, United States')
    print('Finished setup_osm\n')
    
    # Read in output file
    output_file = sys.argv[1]
    crowded_edges = load_output(output_file)

    # Produce figure
    fig, ax = plt.subplots()
    area.plot(ax=ax, facecolor='black')
    buildings.plot(ax=ax, facecolor='khaki', alpha=0.7)
    edges.plot(ax=ax, linewidth=1, edgecolor='white')
    for edge in edges.iterrows():
        u = edge[0][0]
        v = edge[0][1]
        u_v = str(u) + '_' + str(v)

        # Crowded edge
        if u_v in crowded_edges:
            value = crowded_edges[u_v]/20.0
            edge = edges.loc[u].loc[v]
            temp = geopandas.geodataframe.GeoDataFrame(edge, columns=['Name', 'osmid', 'highway', 'oneway', 'length', 'geometry', 'lanes', 'maxspeed', 'service', 'access', 'tunnel', 'junction'])
            temp.plot(ax=ax, linewidth=value, edgecolor='red', zorder=3)
    plt.axis('off')
    plt.xlabel('longitude')
    plt.ylabel('latitude')
    plt.tight_layout()
    plt.savefig('figure.png')    
    print('\nSaved figure')
