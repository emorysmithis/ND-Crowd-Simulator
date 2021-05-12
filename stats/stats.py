#!/usr/bin/env python
import sys 
import pandas as pd
import os
def usage(exitcode): 
    print(f"Usage: {sys.argv[0]} [data file]")
    exit(exitcode)

# get input file 
args = sys.argv
if len(args) < 2: 
    usage(0)
inputfile = args[1] 
print(f"input file: {inputfile}") 

# create data frame from input file 
df = pd.DataFrame() 
df = df.append(pd.read_excel(inputfile), ignore_index=True) 

# sum cols 
max_seats_total = df['Max'].sum() 
open_seats_total = df['Opn'].sum() 
taken_seats_total = max_seats_total - open_seats_total
print(f"max seats: {max_seats_total}, open seats: {open_seats_total}, taken seats: {taken_seats_total}")
ugrad_pop = 8731 
grad_pop = 2200 
print(f"{taken_seats_total} seats / {ugrad_pop + grad_pop} students = {taken_seats_total/(ugrad_pop + grad_pop)} classes per student")

with open('times.txt', 'a') as times: 
    print(df['When'].to_csv(), file=times)
with open('just_times.txt', 'a') as justtimes: 
    print(os.system(f"cat times.txt | grep -Eo '[0-9]+:[0-9]+. - [0-9]+:[0-9]+.' > just_times.txt"), file=justtimes)
