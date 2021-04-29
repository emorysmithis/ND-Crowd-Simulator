#!/usr/bin/env python3

import os
import sys
import multiprocessing as mp

def worker(input_list):
    command = './paths_speeds_simulation.py ' + ' '.join(input_list)
    print(command)
    os.system(command)
    print(f'Finished: {command}')

if __name__ == '__main__':
    
    # Initialize variables
    directories = sys.argv[1:]
    days = ['m', 't', 'w', 'r', 'f']
    #days = ['m'] #TODO: for testing 
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
            #print(input_file) 
            # Run simulation for each combination of arrival early times  
            step = 10
            for time0 in range(0, 110, 10):  
                upper_limit = 100 - time0 + 10
                for time2 in range(0, upper_limit, 10):  
                    upper_limit = 100 - time0 - time2 + 10 
                    for time5 in range(0, upper_limit, 10):
                        upper_limit = 100 - time0 - time2 - time5 + 10  
                        for time10 in range(0, upper_limit, 10): 
                            time15 = 100 - time0 - time2 - time5 - time10 
                            time_arg = str(time0) + '_' + str(time2) + '_' + str(time5) + '_' +  str(time10) + '_' + str(time15) 
                             
                            output_file = d + '/output_' + day + '.txtTEST'
                            process = mp.Process(target=worker, args=(['-s', input_file, '-start', start, '-end', end, '-n', '50', '-speed', speed_arg, '>', output_file],))
                            processes.append(process)
                            process.start()

    for process in processes:
        process.join()

