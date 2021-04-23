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
                [-ugrads num_ugrads (ex: 8000)] 
                [-grads num_grads (ex: 4000)] 
                [-dir output_directory] 
    ''')
    sys.exit(exitcode)

def get_earliest(classes):
    earliest = timeStr2Num("23:59")
    index = -1 
    for i,c in enumerate(classes): 
        start = c['Start'] 
        start = timeStr2Num(start)
        if start < earliest: 
            earliest = start 
            index = i 
    if not earliest: 
        print(f"ERROR: NO EARLIEST CLASS FOUND")
    return index 

def sort_classes(classes): 
    sorted_classes = []
    while len(classes) > 0: 
        index = get_earliest(classes)
        sorted_classes.append(classes[index])
        del classes[index] 
    return sorted_classes

        
def get_dest(dest, dorm): 
    if dest == 'DORM': 
        dest = dorm
    return dest 

def get_journey(classes, day, dorm): 
    day_classes = []
    for c in classes: 
        if day in c['Days']: 
            day_classes.append(c)
    day_classes = sort_classes(day_classes)
    if len(day_classes) < 1: # no classes today, no journey 
        return [] 
    # create journey 
    journeys = []
    # need journey for dorm -> first class 
    first_source = dorm 
    first_target = get_dest(day_classes[0]['Where'], dorm)
    #segments = generate_segments(graph, buildings, first_source, first_target)
    if first_source != first_target: 
        target_time = day_classes[0]['Start']
        journey = {"time": target_time, "source": first_source, "target": first_target}
        journeys.append(journey)
    # rest of paths for day 
    for i,c in enumerate(day_classes): 
        source = get_dest(c['Where'], dorm)
        if i != (len(day_classes)-1): # if not on last class, create journey # TODO: change if to be before 
            target = get_dest(day_classes[i+1]['Where'], dorm) 
            #segments = generate_segments(graph, buildings, source, target)
            if source != target: 
                target_time = day_classes[i+1]['Start']
                journey = {"time": target_time, "source": source, "target": target}
                journeys.append(journey)

    return journeys 

def timeStr2Num(orig):
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
        if check_days_overlap(days, c_days): 
            # since days are the same, need to check times  
            if start >= c_start and start <= c_end: 
                return True
            elif end >= c_start and end <= c_end: 
                return True
            elif c_start >= start and c_end <= end: 
                return True
            #else: #, does not overlap 
        #else: 
    return False 
        
def check_class_full(cdf, num):  
    spec_row = cdf.loc[num]
    if spec_row['Opn'].item() == 0: 
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
    return classes 

def get_dorm(ddf): 
    numDorms = len(ddf.axes[0])
    num = random.randint(0, numDorms-1)
    dorm = ddf.loc[num]['Dorm']
    return dorm 


def create_students(ugrads, grads, cdf, ddf, setup_dir): 
    m_file = setup_dir + '/m_students.txt'
    t_file = setup_dir + '/t_students.txt'
    w_file = setup_dir + '/w_students.txt'
    r_file = setup_dir + '/r_students.txt'
    f_file = setup_dir + '/f_students.txt'
    
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
        sid = grad
        # get classes for student 
        totalNumClasses = len(cdf.axes[0])
        if grad > ugrads-1: 
            myClasses = get_classes(cdf, 2, totalNumClasses)
        else: 
            myClasses = get_classes(cdf, 7, totalNumClasses)
        # get dorm for student 
        dorm = get_dorm(ddf)   
        # create journey 
        m_journey = get_journey(myClasses, "M", dorm)
        t_journey = get_journey(myClasses, "T", dorm)
        w_journey = get_journey(myClasses, "W", dorm)
        r_journey = get_journey(myClasses, "R", dorm)
        f_journey = get_journey(myClasses, "F", dorm)
        # write student to file  
        m_written = write_student(m_written, m_file, sid,  m_journey)
        t_written = write_student(t_written, t_file, sid,  t_journey)
        w_written = write_student(w_written, w_file, sid,  w_journey)
        r_written = write_student(r_written, r_file, sid,  r_journey)
        f_written = write_student(f_written, f_file, sid,  f_journey)
    # end list 
    write_char(m_file, ']')
    write_char(t_file, ']')
    write_char(w_file, ']')
    write_char(r_file, ']')
    write_char(f_file, ']')

def write_char(file_name, mychar): 
    with open(file_name, 'a') as f: 
        f.write(mychar)

def write_student(written, file_name, sid, journey):  
    if len(journey) > 0:
        with open(file_name, 'a') as f:
            if written: # file already has student  
                f.write(',')
            else: # file has no students 
                written = True 
            student = {  
                "id": sid, 
                "journey" : journey
            }  
            f.write(str(json.dumps(student))) 
    return written 

def check_type(var): 
    try: 
        var = int(var) 
        return var 
    except: 
        var = float(var) 
        print(f"WARNING: you input {var} instead of an integer. Rounding {var} to {math.ceil(var)}") 
        return math.ceil(var) 

def main(): 
    # make sure num arguments is correct 
    arguments = sys.argv[1:]
    if len(arguments) < 4: 
        usage(0)
    # set defaults 
    ugrads = 8000 
    grads = 4000
    setup_dir = str(datetime.now()).replace(' ', ':')
    
    # command line parsing 
    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-c':
            class_search_path = arguments.pop(0)
        elif argument == '-d': 
            dorms_path = arguments.pop(0)
        elif argument == '-ugrads': 
            ugrads = int(arguments.pop(0)) 
        elif argument == '-grads': 
            grads = int(arguments.pop(0))  
        elif argument == '-dir': 
            setup_dir = arguments.pop(0) 
        elif argument == '-h':
            usage(0)
        else:
            usage(1)
    
    # ensure input data files exist 
    if not os.path.exists(class_search_path) or not os.path.exists(dorms_path): 
        usage(1)
    print(f"will save output to '{setup_dir}'") 
    if not os.path.exists(setup_dir): 
        try: 
            os.mkdir(setup_dir)  
        except Error as e: 
            print(f"ERROR: cannot create directory '{setup_dir}': {e}") 

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
    
    create_students(ugrads, grads, cdf, ddf, setup_dir)
    cdf.to_excel('full_classes.xlsx')

if __name__ == '__main__': 
    main() 
