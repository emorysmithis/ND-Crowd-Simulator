#!/usr/bin/env python3

import os
import sys
import multiprocessing as mp
from datetime import datetime

def worker(input_list):
    command = './simulation.py ' + ' '.join(input_list)
    print(command)
    os.system(command)
    print(f'finished: {command}')

if __name__ == '__main__':

    # Get start time
    time_start = datetime.now()
    
    # Initialize variables
    directories = sys.argv[1:]
    days = ['m', 't', 'w', 'r', 'f']
    processes = []
    start = ''
    end = ''

    # Iterate through each directory
    for d in directories:

        # Get start_time and end_time
        with open (d+'/time.txt', 'r') as f:
            start = f.readline().strip()
            end = f.readline().strip()

        # Run simulation for each day of the week
        for day in days:
            input_file = d + '/' + day + '_students.txt'
            output_file = d + '/default/output_' + day + '.txt'
            if not os.path.exists(d + '/default'):
                os.mkdir(d + '/default')
            process = mp.Process(target=worker, args=(['-s', input_file, '-start', start, '-end', end, '-n', '50', '>', output_file],))
            processes.append(process)
            process.start()

    for process in processes:
        process.join()

    # Get end time
    time_end = datetime.now()
    tdelta = time_end - time_start
    print('--------TIME--------')
    print('start:', time_start)
    print('end:', time_end)
    print('timedelta:', tdelta)
