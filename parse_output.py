#!/usr/bin/env python3

import os
import sys
from datetime import datetime
import pandas as pd  

def usage(exitcode=0): 
    progname = os.path.basename(sys.argv[0])
    print(f'''Usage: {progname}
                directories 
    ''')
    sys.exit(exitcode)



if __name__ == '__main__':   
    
    # Initialize variables
    files = sys.argv[1:]
    df = pd.DataFrame(columns=['file', 'day', 'time'])
    
    for f in files: 
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
                print("TIME FOUND") 
            elif line.rstrip() == '--------CROWDED EDGES--------': 
                crowded_line_found = True 
                print("CROWDED FOUND") 
            elif line.rstrip() == '--------LATE PERCENTAGE--------': 
                late_line_found = True 
                print("LATE FOUND") 
                crowded_line_found = False 
            elif late_line_found: 
                print(f"late: {line}") 
            elif crowded_line_found: 
                print(f"crowded: {line}") 
                crowded.append(int(line.rstrip().split()[1]))
            elif time_line_found: 
                print(f"time: {line}") 
                '''
                print(f"{output_file_name}:     {line}")
                data = {'dir': d, 'day': day, 'file': output_file_name, 'time': line.rstrip()} 
                df = df.append(data, ignore_index = True)  
                time_line_found = False
                '''

    '''
    myformat = '%H:%M:%S.%f'
    df['time'] = pd.to_timedelta(df['time'])
    
    #df['time'] = pd.to_datetime(df['time']).dt.time
    print(df) 
    times_list = list(df['time'])
    print(times_list)
    '''

