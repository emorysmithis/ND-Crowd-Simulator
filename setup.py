#!/usr/bin/env python 

import pandas as pd 
import os 
import sys 

def usage(exitcode=0): 
    progname = os.path.basename(sys.argv[0])
    print(f'''Usage: {progname} -c class_search.xlsx
    ''')
    sys.exit(exitcode)

def get_journey(): 
    journey = [
        {
            "time": "8:00",
            "segments": [
                {
                    "path_index": 1,
                    "edge_id": 1001,
                    "edge_length": 20
                },
                {
                    "path_index": 2,
                    "edge_id": 1100,
                    "edge_length": 3
                }
            ]
        },
        {
            "time": "9:00",
            "segments": [
                {
                    "path_index": 1,
                    "edge_id": 765,
                    "edge_length": 90
                }
            ]
    
        }
    ]   
    return journey 

def get_speed(): 
    return 1 

def create_students(ugrads, grads): 
    students = []
    for grad in range(ugrads+grads): 
        # create dicts
        sid = grad
        speed = get_speed() 
        journey = get_journey() 
        student = { 
            "id": sid,
            "speed": speed,
            "edge_index": -1, 
            "journey": journey
        } # end of student dict 
        students.append(student)
    print(students)
    return students 

def main(): 
    # command line parsing 
    arguments = sys.argv[1:]
    if len(arguments) < 2: 
        usage(0)
    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-c':
            class_search_path = arguments.pop(0)
        elif argument == '-h':
            usage(0)
        else:
            usage(1)
    # create students 
    ugrads = 8500 
    grads  = 4000
    students = create_students(ugrads, grads)
    print(students, file=open("students.txt", "a"))


if __name__ == '__main__': 
    main() 
