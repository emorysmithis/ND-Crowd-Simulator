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
            # Run simulation for each combination of paths 
            step = 10
            for fp1 in range(30, 110, 10): # TODO: changed 110 to 50  
                upper_limit = 100 - fp1 + 10
                for fp2 in range(0, upper_limit, 10): # TODO: changed upper_limit to 20 
                    fp_arg = str(fp1) + '_' + str(fp2)
                    #print(fp_arg) 
            
                    output_file = d + '/output_' + day + '_' + fp_arg + '.txt'
                    process = mp.Process(target=worker, args=(['-s', input_file, '-start', start, '-end', end, '-n', '50', '-fp', fp_arg, '>', output_file],))
                    processes.append(process)
                    process.start()
                
                for process in processes:
                    process.join()
                print("joined one set") 
                processes = [] 
