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
    directories = sys.argv[1:]
    days = ['m', 't', 'w', 'r', 'f']
    df = pd.DataFrame(columns=['dir', 'day','file', 'time'])
    
    for d in directories: 
        for day in days: 
            output_file_name = d + "/output_" + day + ".txt" 
            output_file = open(output_file_name, 'r')
            time_line_found = False  
            for line in output_file:
                if line.rstrip() == '--------TIME--------':
                    time_line_found = True 
                elif time_line_found: 
                    print(f"{output_file_name}:     {line}")
                    data = {'dir': d, 'day': day, 'file': output_file_name, 'time': line.rstrip()} 
                    df = df.append(data, ignore_index = True)  
                    time_line_found = False
    myformat = '%H:%M:%S.%f'
    df['time'] = pd.to_timedelta(df['time'])
    
    #df['time'] = pd.to_datetime(df['time']).dt.time
    print(df) 
    times_list = list(df['time'])
    print(times_list)
  
