#!/usr/bin/env python3

import sys
import os
import json
import osmnx as ox
import math
from datetime import time, timedelta, datetime, date
from random import randint

def setup_osm(place_name): 
    graph = ox.graph_from_place(place_name)
    buildings = ox.geometries_from_place(place_name, tags={'building':True})
    buildings_dict = {}
    for index, row in buildings.iterrows():
        if row['name'] not in buildings_dict:
            buildings_dict[row['name']] = {}
            buildings_dict[row['name']]['x'] = float('-' + str(row['geometry']).split('-')[1].split(' ')[0])
            buildings_dict[row['name']]['y'] = float(str(row['geometry']).split('-')[1].split(' ')[1].split(',')[0][:-1])
    return graph,buildings_dict

def generate_segments(graph, buildings_dict, s_building, t_building, path_num):
    # Make sure source != target 
    if s_building == t_building: 
        return []

    nodes, edges = ox.graph_to_gdfs(graph)

    # Get starting node
    try: 
        x = buildings_dict[s_building]['x']
        y = buildings_dict[s_building]['y']        
        orig_node = ox.get_nearest_node(graph, (y, x))

        # Get destination node
        x = buildings_dict[t_building]['x']
        y = buildings_dict[t_building]['y']        
        target_node = ox.get_nearest_node(graph, (y, x))

        # Create path
        node_list = ox.distance.k_shortest_paths(graph, orig_node, target_node, 3) 
        node_list = list(node_list)[path_num]
        #node_list = ox.distance.shortest_path(graph, orig_node, target_node)

        # Create segments list
        segments = []
        for i, (u, v) in enumerate(list(zip(node_list[:-1], node_list[1:]))):
            edge = graph.get_edge_data(u, v)

            # Find dictionary parameters
            path_index = i + 1 #TODO: change this to zero indexing 
            edge_id = edge[0]['osmid']
            if isinstance(edge_id, list):
                edge_id = edge_id[0]
            edge_length = math.ceil(edge[0]['length'])

            # Set dictionary parameters
            segment = {}
            segment['path_index'] = path_index
            segment['edge_id'] = edge_id
            segment['edge_length'] = edge_length
            segments.append(segment)
    except Exception as e: 
        print(f"ERROR DURING |{s_building}| {e}")
        
    return segments

def load_students(students_file, speed_list):
    table = []          # master list of students

    with open(students_file) as data:
        table = json.load(data)

    for student in table:
        student['edge_index'] = -1
        # Set speed
        value = randint(0, 100)
        if value < speed_list[0]: # walk 
            student['speed'] = 1
        elif value < speed_list[0] + speed_list[1]: # scooter 
            student['speed'] = 3
        else: # biking 
            student['speed'] = 5
    return table

def add_edgeid(D, edge_id):
    if edge_id not in D:            # if edge_id not in dictionary
        D[edge_id] = 0
    D[edge_id] += 1                 # increment count
    return D

def usage(exitcode=0): 
    progname = os.path.basename(sys.argv[0])
    print(f'''Usage: {progname}
                -s students.txt 
                -start start_time (ex: 7:30) 
                -end end_time (ex: 23:59) 
                -n N (top N crowded paths ex: 50) 
                [-fp (percentage of students who take the fastest paths) ex: 80_10 (80% 1st fastest, 10% 2nd fastest, 10% 3rd fastest)]
                [-speed percentage of people walking, scootering, biking ex: 80_10_10] 
    ''')
    sys.exit(exitcode)

def calc_fp3(fp1, fp2): 
    if fp1 + fp2 > 100: 
        print(f"{fp1} + {fp2} > 100") 
        sys.exit(1) 
    return 100 - fp1 - fp2

def get_path_num(fp1, fp2, fp3): 
    rand = randint(1, 100) 
    #print(f"rand: {rand}") 
    if rand <= fp1: 
        return 0 
    elif rand <= fp2: 
        return 1 
    elif rand <= fp3: 
        return 2 

# Main function
if __name__ == '__main__':
    
    # Get start time
    time_start = datetime.now()
    

    # make sure num arguments is correct 
    arguments = sys.argv[1:]
    if len(arguments) < 8: # 1 for each flag + 1 for the corresponding arg 
        usage(0)
    
    # set default vals 
    fp1 = 100 
    fp2 = 0 
    fp3 = 0 
    speed_list = [100, 0, 0]
    # command line parsing 
    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-s':
            students_file = arguments.pop(0)
        elif argument == '-start': 
            h, m = arguments.pop(0).split(':') 
            curr_time = time(int(h), int(m), 0)
        elif argument == '-end': 
            h, m = arguments.pop(0).split(':')  
            end_time = time(int(h), int(m), 0)
        elif argument == '-n': 
            N = int(arguments.pop(0))  
        elif argument == '-fp': 
            fp1, fp2 = arguments.pop(0).split('_') # determine the weights for shortest k paths  
            fp1 = int(fp1) 
            fp2 = int(fp2) 
            fp3 = calc_fp3(fp1, fp2) 
            #print(f"1f_per: {fp1}, 2f_per: {fp2}, 3f_per: {fp3}") 
            fp2 = fp1 + fp2 
            fp3 = fp2 + fp3 
        elif argument == '-speed': 
            speed1, speed2, speed3 = arguments.pop(0).split('_') 
            speed_list = [int(speed1), int(speed2), int(speed3)]
        elif argument == '-h':
            usage(0)
        else:
            usage(1)    
    
    print(f"students file: {students_file}, start: {curr_time}, end: {end_time}, N: {N}") 

    # Data
    crowding_dict = {}
    graph, buildings_dict = setup_osm('Notre Dame, Indiana, United States') 
    table = load_students(students_file, speed_list)

    # Main loop
    while curr_time != end_time:
        curr_dict = {}

        # Iterate through each student
        for student in table:
            edge_index = student['edge_index']
            
            # Student is currently walking
            if edge_index >= 0:

                # Student should continue walking along edge
                if edge_index < student['journey'][0]['segments'][0]['edge_length']:
                    student['edge_index'] += student['speed']
                    add_edgeid(curr_dict, student['journey'][0]['segments'][0]['edge_id'])
                # Student should change to a new edge
                elif len(student['journey'][0]['segments']) > 1:
                    student['journey'][0]['segments'].pop(0)
                    student['edge_index'] = student['speed']
                    add_edgeid(curr_dict, student['journey'][0]['segments'][0]['edge_id'])
                # Student has arrived at destination
                else:
                    student['journey'].pop(0)
                    student['edge_index'] = -1
            
            # Student is not currently walking
            elif len(student['journey']):
            
                # Calculate estimated time to get to class
                estimated_time = 0
                if not 'segments' in student['journey'][0]:
                    path_num = get_path_num(fp1, fp2, fp3) 
                    #print(f"path num: {path_num}") 
                    student['journey'][0]['segments'] = generate_segments(graph, buildings_dict, student['journey'][0]['source'], student['journey'][0]['target'], path_num)
                for t in student['journey'][0]['segments']:
                    estimated_time += t['edge_length']
                estimated_time /= student['speed']

                h, m = student['journey'][0]['time'].split(':')
                class_time = time(int(h), int(m), 0)

                # Student should start moving
                if (datetime.combine(date(1,1,1),class_time) - timedelta(minutes=2, seconds=estimated_time)).time() < curr_time:
                    student['edge_index'] = student['speed']
                    add_edgeid(curr_dict, student['journey'][0]['segments'][0]['edge_id'])
        
        # Update crowding_dict
        for edge_id, value in curr_dict.items():
            if edge_id not in crowding_dict:
                crowding_dict[edge_id] = value
            elif value > crowding_dict[edge_id]:
                crowding_dict[edge_id] = value
    
        # Update curr_time
        curr_time = (datetime.combine(date(1,1,1),curr_time) + timedelta(seconds=1)).time()
   
    # Print N most crowded edges 
    print('--------CROWDED EDGES--------')
    crowding_dict = {k: v for k, v in sorted(crowding_dict.items(), key=lambda item: item[1], reverse=True)}
    for i, (key, value) in enumerate(crowding_dict.items()):
        if i < N:
            print(key, value)

    # Get end time
    time_end = datetime.now()
    tdelta = time_end - time_start
    print('--------TIME--------')
    print(tdelta)

    
