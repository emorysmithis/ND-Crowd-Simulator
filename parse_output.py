#!/usr/bin/env python3

import os
import sys
from datetime import datetime
import pandas as pd 
import re 

def usage(exitcode=0): 
    progname = os.path.basename(sys.argv[0])
    print(f'''Usage: {progname}
                -o parse_output_file_name.xlsx
                [-df input_data_frame.xlsx] (can't be same as -o) 
                output files  
    ''')
    sys.exit(exitcode)

def add_crowded(crowded, data): 
    max_crowd = max(crowded) 
    avg_crowd = sum(crowded)/50 
    data['max_crowd'] = max_crowd
    data['avg_crowd'] = avg_crowd
    return data 

def add_row(data, df): 
    df = df.append(data, ignore_index = True)  
    return df 

def get_day(f): 
    filename = f.split(r'/')[-1]
    day = filename.split('_')[1]
    if '.txt' in day: 
        day = day[0] 
    if day not in ['m', 't', 'w', 'r', 'f']: 
        print(f"ERROR: {day} not in Days!")
        exit(1)
    return day 

def add_late(data, line): 
    if 'percent' in line: 
        percent = line.split(':')[1].lstrip() 
        data['percent_late'] = percent 
    elif 'number' in line: 
        number = int(line.split(':')[1].lstrip())
        data['num_late'] = number
    elif 'total' in line:  
        total = line.split(':')[1].lstrip() 
        data['total_classes'] = total
    return data 

def add_time(data, line): 
    data['time'] = line #TODO: add total seconds
    line = line.split('.')[0] 
    line = line.split(':')
    print(line) 
    hours = int(line[0]) 
    mins = int(line[1]) 
    secs = int(line[2]) 
    total_sec = hours*60*60 + mins*60 + secs 
    data['total_sec'] = total_sec 
    return data

def get_pop(f): 
    regex = (r'([0-9]+)_students') 
    matches = re.findall(regex, f) 
    if len(matches) > 1: 
        print(f"len(matches) > 1! matches: {matches}. choosing {matches[0]}")
    return matches[0] 

def get_type(f): 
    if 'default' in f and 'parallel' in f: 
        return 0
    elif 'path' in f and 'parallel' in f: 
        return 1
    elif 'path' in f and 'batch' in f: 
        return 2 
    elif 'speed' in f: 
        return 3
    elif 'local' in f: 
        return 4 
    elif 'path' in f: 
        return 5 
    elif 'default' in f: 
        return 6
    else: 
        return 'ERROR' 

if __name__ == '__main__':   
    
    # make sure num args correct 
    arguments = sys.argv[1:] 
    if len(arguments) < 3: # -o output_file files
        usage(0) 

    # Initialize variables
    input_df  = False 

    # command line parsing 
    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-o':
            output_file_name = arguments.pop(0)  
            print(f"output file: {output_file_name}") 
            output_file = open(output_file_name, 'w+') 
        elif argument == '-df':
            df_name = str(arguments.pop(0)) 
            print(f"data frame input: {df_name}") #TODO make sure file exists 
            df = pd.read_excel(df_name) 
            input_df = True 
        elif argument == '-h':
            usage(0)
        else:
            usage(1)    
    files = arguments 
    if not input_df:
        print(f"input dataframe not given!") 
        df = pd.DataFrame(columns=['file', 'day', 'pop', 'type', 'time', 'total_sec', 'max_crowd', 'avg_crowd', 'percent_late', 'num_late', 'total_classes'])
    
    for f in files:
        print(f) 
        pop = get_pop(f)  
        day = get_day(f) 
        sim_type = get_type(f) 
        data = {'day': day, 'file': f, 'pop': pop, 'type': sim_type} 
        output_file = open(f, 'r')
        time_line_found     = False  
        crowded_line_found  = False
        late_line_found     = False 
        crowded = [] 
        for line in output_file:
            line = line.rstrip() 
            if line.rstrip() == '--------TIME--------':
                time_line_found = True
                late_line_found = False 
            elif line.rstrip() == '--------CROWDED EDGES--------': 
                crowded_line_found = True 
            elif line.rstrip() == '--------LATE PERCENTAGE--------': 
                late_line_found = True 
                data = add_crowded(crowded, data)  
                crowded_line_found = False 
            elif late_line_found: 
                data = add_late(data, line) 
            elif crowded_line_found: 
                crowded.append(int(line.rstrip().split()[1]))
            elif time_line_found:
                data = add_time(data, line) 

        # end of file 
        # print(data) 
        df = add_row(data, df) 

   
    df.to_excel(f"{output_file_name}") 



