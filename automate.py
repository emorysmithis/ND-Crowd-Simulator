#!/usr/bin/env python3

import os
import sys
import multiprocessing as mp

def worker(input_file, start, end, N, output_file):
    command = './simulation.py ' + input_file + ' ' + start + ' ' + end + ' ' + N ' > ' + output_file
    os.system(command)
    print('finished')

print("Number of processors: ", mp.cpu_count())
if __name__ == '__main__':
    
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
            start, end = f.readline().strip().split()

        # Run simulation for each day of the week
        for day in days:
            input_file = d + '/' + day + '_students.txt'
            output_file = d + '/output_' + day + '.txt'
            process = mp.Process(target=worker, args=(input_file, start, end, '50', output_file))
            processes.append(process)
            process.start()

    for process in processes:
        process.join()

