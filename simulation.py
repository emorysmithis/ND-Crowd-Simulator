#!/usr/bin/env python3

import os
import json
from datetime import time, timedelta, datetime, date

def load_students():
    table = []          # master list of students

    # Get list of json file names
    json_files = [json_file for json_file in os.listdir('./') if json_file.endswith('.json')]

    # Load student data into table
    for json_file in json_files:
        with open(json_file) as data:
            student = json.load(data)
            table.append(student)

    return table

def remove_files():
    json_files = [json_file for json_file in os.listdir('./') if json_file.endswith('.json')]
    for json_file in json_files:
        os.remove(json_file)


# Main function
if __name__ == '__main__':

    # Initialize parameters
    table = load_students()
    curr_time = time(7, 45, 0)              # TODO: determine start time -> 8 am
    end_time = time(12, 5, 0)               # TODO: determine end time -> 8 pm
    crowding_dict = {}

    # Main loop
    while curr_time != end_time:
        print(curr_time)

        # Iterate through each student
        for student in table:
            edge_index = student['edge_index']
            
            # Student is currently walking
            if edge_index >= 0:

                # Student should continue walking along edge
                if edge_index < student['journey'][0]['segments'][0]['edge_length']:
                    student['edge_index'] += student['speed']
                    print(curr_time, student['id'], student['journey'][0]['segments'][0]['path_index'], student['edge_index'])
                # Student should change to a new edge
                elif len(student['journey'][0]['segments']) > 1:
                    student['journey'][0]['segments'].pop(0)
                    student['edge_index'] = student['speed']
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
                    print(curr_time, student['id'], student['journey'][0]['segments'][0]['path_index'], student['edge_index'])
            
        # Update curr_time
        curr_time = (datetime.combine(date(1,1,1),curr_time) + timedelta(seconds=1)).time()
        

    # Remove files
    #remove_files()             # TODO: uncomment later
