#!/usr/bin/env python 

import pandas as pd 
import os 
import sys 
import random 
from datetime import datetime 
import osmnx as ox
import math 
import json

def usage(exitcode=0): 
    progname = os.path.basename(sys.argv[0])
    print(f'''Usage: {progname} -c class_search.xlsx 
                -d dorms.xlsx
    ''')
    sys.exit(exitcode)

def get_earliest(classes):
    earliest = timeStr2Num("23:59")
    #print(f"original earliest: {earliest}")
    index = -1 
    for i,c in enumerate(classes): 
        start = c['Start'] 
        start = timeStr2Num(start)
        #print(f"comparing {start} and {earliest}")
        if start < earliest: 
            #print(f"{start} < {earliest}")
            earliest = start 
            index = i 
    if not earliest: 
        print(f"ERROR: NO EARLIEST CLASS FOUND")
    #print(f"earliest: {classes[index]}")
    return index 

def sort_classes(classes): 
    sorted_classes = []
    #print(f"original classes: {classes}")
    while len(classes) > 0: 
        index = get_earliest(classes)
        sorted_classes.append(classes[index])
        del classes[index] 
    #print(f"sorted classes: {sorted_classes}")
    return sorted_classes

        
def get_dest(dest, dorm): 
    if dest == 'DORM': 
        dest = dorm
    return dest 

def get_journey(graph, buildings, classes, day, dorm): 
    #print(f"CHECKING  which classes in: {classes} are on day: {day}\n")
    day_classes = []
    for c in classes: 
        if day in c['Days']: 
            day_classes.append(c)
    #print(f"{day_classes} classes are on {day}")
    day_classes = sort_classes(day_classes)
    if len(day_classes) < 1: # no classes today, no journey 
        return [] 
   # print(day)
    journeys = []
    # need journey for dorm -> first class 
    first_source = dorm 
    first_target = get_dest(day_classes[0]['Where'], dorm)
    #print(f"Go from {first_source} to {first_target}")
    segments = generate_segments(graph, buildings, first_source, first_target)
    #print(f"by following {segments}")
    if len(segments) > 0: 
        #print("adding path to journey")
        target_time = day_classes[0]['Start']
        journey = {"time": target_time, "segments": segments}
        journeys.append(journey)
    # rest of paths for day 
    for i,c in enumerate(day_classes): 
        #print(f"{i}. {c}")
        source = get_dest(c['Where'], dorm)
        if i != (len(day_classes)-1): # if not on last class, create journey # TODO: change if to be before 
            target = get_dest(day_classes[i+1]['Where'], dorm) 
            #print(f"{source} -> {target}")
            segments = generate_segments(graph, buildings, source, target)
            if len(segments) > 0: 
                target_time = day_classes[i+1]['Start']
                journey = {"time": target_time, "segments": segments}
                journeys.append(journey)

    return journeys 

def get_speed(): 
    return 1 

def timeStr2Num(orig):
    #print(orig)
    hour, mins = orig.split(':')
    return ((int(hour)*60) + int(mins))

def check_days_overlap(days1, days2): 
    for letter in days1: 
        if letter in days2:
            return True
    return False 

def check_time_overlap(classes, start, end, days):
    #print(f"in check time overlap")
    start = timeStr2Num(start)
    end = timeStr2Num(end)
    for c in classes: 
        c_start = timeStr2Num(c['Start'])
        c_end = timeStr2Num(c['End']) 
        c_days = c['Days']
        if check_days_overlap(days, c_days): 
            #print(f"days same!")
            # since days are the same, need to check times  
            if start >= c_start and start <= c_end: 
                #print(f"{start} in between {c['Start']} and {c['End']}")
                return True
            elif end >= c_start and end <= c_end: 
                #print(f"{end} in between {c['Start']} and {c['End']}")
                return True
            elif c_start >= start and c_end <= end: 
                #print(f"{start} {end} contained in {c_start} {c_end}")
                return True
            #else: #, does not overlap 
                #print(f"{start} {end} does not overlap {c_start} {c_end}")
        #else: 
            #print("days not the same, moving on to next class")
    return False 
        
def check_class_full(cdf, num):  
    spec_row = cdf.loc[num]
    if spec_row['Opn'].item() == 0: 
        #print(f"{spec_row['Course - Sec']} is FULL") 
        return True # class is full :( 
    else: 
        return False # class is not full :) 


def get_classes(cdf, numClasses, totalNumClasses): 
    classes = []
    class_indicies = [] 
    c = 0 
    while len(classes) < numClasses: 
        num = random.randint(0, totalNumClasses-1)
        if num not in class_indicies:  
            class_indicies.append(num) 
            course = cdf.loc[num]
            course = {"crn": course['Course - Sec'], "Days": course['Days'], "Start": course['Start Time'], "End": course['End Time'], "Where": course['Where']}
            if type(course["Start"]) != float: 
                if not check_time_overlap(classes, course["Start"], course["End"], course['Days']) and not check_class_full(cdf, num): # make sure classes not at same time/day and not full
                    #print(f"adding {course}")
                    classes.append(course)
                    c += 1 
                    cdf.at[num, 'Opn'] =  cdf.at[num, 'Opn'] - 1 # decrease number of open seats 
    #print(classes)
    return classes 

def get_dorm(ddf): 
    numDorms = len(ddf.axes[0])
    num = random.randint(0, numDorms-1)
    dorm = ddf.loc[num]['Dorm']
    return dorm 

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

def generate_segments(graph, buildings_dict, s_building, t_building):
    # Make sure source != target 
    if s_building == t_building: 
        return [] 
    nodes, edges = ox.graph_to_gdfs(graph)
    # Get starting node
    try: 
        #print(f"the thing messing me up: {buildings.loc[buildings['name'] == s_building].iloc[0]}")
        x = buildings_dict[s_building]['x']
        y = buildings_dict[s_building]['y']        
        orig_node = ox.get_nearest_node(graph, (y, x))

        # Get destination node
        x = buildings_dict[t_building]['x']
        y = buildings_dict[t_building]['y']        
        target_node = ox.get_nearest_node(graph, (y, x))

        # Create path
        node_list = ox.distance.shortest_path(graph, orig_node, target_node)

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
        
    #return [] 
    return segments

def create_students(ugrads, grads, cdf, ddf, graph, buildings): 
    #students = []
    m_file = 'm_students.txt'
    t_file = 't_students.txt'
    w_file = 'w_students.txt'
    r_file = 'r_students.txt'
    f_file = 'f_students.txt'
    
    write_char(m_file, '[')
    write_char(t_file, '[')
    write_char(w_file, '[')
    write_char(r_file, '[')
    write_char(f_file, '[')
    
    m_written = False 
    t_written = False 
    w_written = False 
    r_written = False 
    f_written = False 
    
    for grad in range(ugrads+grads):
        print(grad)
        # create dicts
        sid = grad
        speed = get_speed() 
        # get classes for student 
        totalNumClasses = len(cdf.axes[0])
        if grad > ugrads-1: 
            myClasses = get_classes(cdf, 2, totalNumClasses)
            #print(myClasses)
        else: 
            myClasses = get_classes(cdf, 7, totalNumClasses)
            #print(myClasses)
        # get dorm for student 
        dorm = get_dorm(ddf)   
        # create journey 
        m_journey = get_journey(graph, buildings, myClasses, "M", dorm)
        t_journey = get_journey(graph, buildings, myClasses, "T", dorm)
        w_journey = get_journey(graph, buildings, myClasses, "W", dorm)
        r_journey = get_journey(graph, buildings, myClasses, "R", dorm)
        f_journey = get_journey(graph, buildings, myClasses, "F", dorm)
        '''
        student = { 
            "id": sid,
            "speed": speed,
            "edge_index": -1, 
            "m_journey": m_journey, 
            "t_journey": t_journey, 
            "w_journey": w_journey, 
            "r_journey": r_journey, 
            "f_journey": f_journey, 
        } # end of student dict
        '''
        #students.append(student)
        m_written = write_student(m_written, m_file, sid, speed, m_journey)
        t_written = write_student(t_written, t_file, sid, speed, t_journey)
        w_written = write_student(w_written, w_file, sid, speed, w_journey)
        r_written = write_student(r_written, r_file, sid, speed, r_journey)
        f_written = write_student(f_written, f_file, sid, speed, f_journey)

    #return students 
    write_char(m_file, ']')
    write_char(t_file, ']')
    write_char(w_file, ']')
    write_char(r_file, ']')
    write_char(f_file, ']')

def write_char(file_name, mychar): 
    with open(file_name, 'a') as f: 
        f.write(mychar)

def write_student(written, file_name, sid, speed, journey):  
    if len(journey) > 0:
        with open(file_name, 'a') as f:
            if written: # file already has student  
                f.write(',')
            else: # file has no students 
                written = True 
            student = {  
                "id": sid,
                "speed": speed,
                "edge_index": -1, 
                "journey" : journey
            }  
            f.write(str(json.dumps(student))) 
    return written 

def main(): 
    # command line parsing 
    arguments = sys.argv[1:]
    if len(arguments) < 4: 
        usage(0)
    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-c':
            class_search_path = arguments.pop(0)
        elif argument == '-d': 
            dorms_path = arguments.pop(0)
        elif argument == '-h':
            usage(0)
        else:
            usage(1)

    # ensure input data files exist 
    if not os.path.exists(class_search_path) or not os.path.exists(dorms_path): 
        usage(1)
    
    # create class_search data frame 
    cdf = pd.DataFrame() 
    cdf = cdf.append(pd.read_excel(class_search_path), ignore_index=True)  
    if cdf['Max'].all() != cdf['Opn'].all(): 
        print(f"Max seats and Open seats not equal!")
    
    # create dorms data frame 
    ddf = pd.DataFrame() 
    ddf = ddf.append(pd.read_excel(dorms_path), ignore_index=True)
    ddf = ddf.drop('Unnamed: 0', 1)
    ddf = ddf.rename(columns={0: 'Dorm'})
    
    # setup osmnx 
    place_name = 'Notre Dame, Indiana, United States'
    graph, buildings = setup_osm(place_name)
    

    # create students
    #ugrads = 10 
    #grads  = 2
    ugrads = 8000 
    grads  = 4000

    #students = create_students(ugrads, grads, cdf, ddf, graph, buildings)
    create_students(ugrads, grads, cdf, ddf, graph, buildings)
    cdf.to_excel('full_classes.xlsx')

if __name__ == '__main__': 
    main() 
