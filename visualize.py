#!/usr/bin/env python3

import sys
import osmnx as ox
import matplotlib.pyplot as plt
import geopandas
import math 

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
            if 'LATE PERCENTAGE' in line: 
                break 
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
    fig, ax = plt.subplots(figsize=(20,20))
    area.plot(ax=ax, facecolor='white')
    buildings.plot(ax=ax, facecolor='khaki', alpha=0.7)
    edges.plot(ax=ax, linewidth=1, edgecolor='khaki')
    for edge in edges.iterrows():
        u = edge[0][0]
        v = edge[0][1]
        u_v = str(u) + '_' + str(v)

        # Crowded edge
        if u_v in crowded_edges: 
            value = crowded_edges[u_v]/75.0
            edge = edges.loc[u].loc[v]
            # get max crowding 
            max_value = max(crowded_edges.values()) 
            print(f"max val: {max_value}") 
            # set color vals 
            red_val = pow(crowded_edges[u_v],4)  / pow(max_value,4) 
            blue_val = 1 - (red_val) 
            green_val = 0
            print(red_val, blue_val) 
            # graph 
            temp = geopandas.geodataframe.GeoDataFrame(edge, columns=['Name', 'osmid', 'highway', 'oneway', 'length', 'geometry', 'lanes', 'maxspeed', 'service', 'access', 'tunnel', 'junction'])
            temp.plot(ax=ax, linewidth=value, edgecolor=(red_val, green_val, blue_val), zorder=3)
            #temp.plot(ax=ax, linewidth=value, edgecolor='red', zorder=3)
    plt.axis('off')
    plt.xlabel('longitude')
    plt.ylabel('latitude')
    plt.tight_layout()

    fig_name = sys.argv[2]
    plt.savefig(fig_name)    
    print(f'\nSaved figure to {fig_name}')
