#!/usr/bin/env python3

import os
import json
from datetime import time, timedelta, datetime, date

def load_students(students_file):
    table = []          # master list of students

    with open(students_file) as data:
        table = json.load(data)
    return table

def add_edgeid(D, edge_id):
    if edge_id not in D:            # if edge_id not in dictionary
        D[edge_id] = 0
    D[edge_id] += 1                 # increment count
    return D

def remove_files():
    json_files = [json_file for json_file in os.listdir('./') if json_file.endswith('.json')]
    for json_file in json_files:
        os.remove(json_file)


# Main function
if __name__ == '__main__':

    # Initialize parameters
    students_file = 'm_students.txt'        # TODO: commandline argument
    curr_time = time(7, 30, 0)              # TODO: determine start time -> 8 am
    end_time = time(23, 5, 0)               # TODO: determine end time -> 8 pm
    N = 3                                   # TODO: set N accordingly
    crowding_dict = {}
    table = load_students(students_file)

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
                    print(curr_time, student['id'], student['journey'][0]['segments'][0]['path_index'], student['edge_index'])
                # Student should change to a new edge
                elif len(student['journey'][0]['segments']) > 1:
                    student['journey'][0]['segments'].pop(0)
                    student['edge_index'] = student['speed']
                    add_edgeid(curr_dict, student['journey'][0]['segments'][0]['edge_id'])
                    print(curr_time, student['id'], student['journey'][0]['segments'][0]['path_index'], student['edge_index'])
                # Student has arrived at destination
                else:
                    student['journey'].pop(0)
                    student['edge_index'] = -1
            
            # Student is not currently walking
            elif len(student['journey']):
            
                # Calculate estimated time to get to class
                estimated_time = 0
                for t in student['journey'][0]['segments']:
                    estimated_time += t['edge_length']
                estimated_time /= student['speed']

                h, m = student['journey'][0]['time'].split(':')
                class_time = time(int(h), int(m), 0)

                # Student should start moving
                if (datetime.combine(date(1,1,1),class_time) - timedelta(minutes=2, seconds=estimated_time)).time() < curr_time:
                    student['edge_index'] = student['speed']
                    add_edgeid(curr_dict, student['journey'][0]['segments'][0]['edge_id'])
                    print(curr_time, student['id'], student['journey'][0]['segments'][0]['path_index'], student['edge_index'])
        
        # Update crowding_dict
        for edge_id, value in curr_dict.items():
            if edge_id not in crowding_dict:
                crowding_dict[edge_id] = value
            elif value > crowding_dict[edge_id]:
                crowding_dict[edge_id] = value
    
        # Update curr_time
        curr_time = (datetime.combine(date(1,1,1),curr_time) + timedelta(seconds=1)).time()
   
    # Print N most crowded edges 
    crowding_dict = {k: v for k, v in sorted(crowding_dict.items(), key=lambda item: item[1], reverse=True)}
    for i, (key, value) in enumerate(crowding_dict.items()):
        if i < N:
            print(key, value)
            

    # Remove files
    #remove_files()             # TODO: uncomment later
