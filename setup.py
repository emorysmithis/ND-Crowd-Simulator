#!/usr/bin/env python 

import pandas as pd 
import os 
import sys 
import random 
from datetime import datetime 

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
    start = timeStr2Num(start)
    end = timeStr2Num(end)
    for c in classes: 
        c_start = timeStr2Num(c['Start'])
        c_end = timeStr2Num(c['End']) 
        c_days = c['Days']
        if not check_days_overlap(days, c_days): 
            return False # days not the same, so don't need to check times 
        if start >= c_start and start <= c_end: 
            #print(f"{start} in between {c['Start']} and {c['End']}")
            return True
        elif end >= c_start and end <= c_end: 
            #print(f"{end} in between {c['Start']} and {c['End']}")
            return True
        elif c_start >= start and c_end <= end: 
            #print(f"{start} {end} contained in {c_start} {c_end}")
            return True
        # else, does not overlap 
    return False 
        
def check_class_full(cdf, num):  
    spec_row = cdf.loc[num]
    #print(f"ROW: {spec_row}")
    #print(f"OPEN SEATS: {spec_row['Opn']}")
    #print(f"TYPE: {type(spec_row['Opn'].item())}")
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
                    classes.append(course)
                    c += 1 
                    cdf.at[num, 'Opn'] =  cdf.at[num, 'Opn'] - 1 # decrease number of open seats 
    #print(classes)
    return classes

def create_students(ugrads, grads, cdf): 
    students = []
    for grad in range(ugrads+grads):
        print(grad)
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
        totalNumClasses = len(cdf.axes[0])
        if grad > ugrads: 
            myClasses = get_classes(cdf, 2, totalNumClasses)
        else: 
            myClasses = get_classes(cdf, 7, totalNumClasses)
        #print(myClasses)
        students.append(student)
    #print(students)
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

    # ensure input data files exist 
    if not os.path.exists(class_search_path): 
        usage(1)
    
    # create class_search data frame 
    cdf = pd.DataFrame() 
    cdf = cdf.append(pd.read_excel(class_search_path), ignore_index=True)  
    if cdf['Max'].all() != cdf['Opn'].all(): 
        print(f"Max seats and Open seats not equal!")
        
    # create students
    #ugrads = 500 
    #grads  = 400 
    ugrads = 8000 
    grads  = 4000

    students = create_students(ugrads, grads, cdf)
    print(students, file=open("students.txt", "a"))
    cdf.to_excel('full_classes.xlsx')

if __name__ == '__main__': 
    main() 
