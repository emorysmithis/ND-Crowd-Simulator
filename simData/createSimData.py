#!/usr/bin/env python 

import sys 
import pandas as pd
import os
import re 

def usage(exitcode=0): 
    progname = os.path.basename(sys.argv[0])
    print(f'''Usage: {progname} -d data_file.xlsx -o output_data.xlsx []
    -d input_data_path      Data file to use as base 
    -o output_data_path     Output data file''')
    sys.exit(exitcode)

def adjust_when(df): # TODO: need to account for sections () 
    # add a day column 
    df['Days'] = ""
    for index,row in df.iterrows():
        if row['When'][0:3] != "TBA":
            orig = row['When']
            noSpaces = orig.replace(" ", "")
            regex = r'([A-Z]+)-.*'  # get the days from the When col 
            days = re.findall(regex,noSpaces)
            df.loc[index, 'Days'] = days # set the days in the Days col 
    return df 


def main(): 
    # command line parsing 
    arguments = sys.argv[1:]
    if len(arguments) < 4: 
        usage(0)
    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-d':
            input_data_path = arguments.pop(0)
        elif argument == '-o':
            output_data_path = arguments.pop(0)
        elif argument == '-h':
            usage(0)
        else:
            usage(1)
    
    # ensure input data file exists 
    if not os.path.exists(input_data_path):
        usage(1)
    
    # create data frame 
    df = pd.DataFrame() 
    df = df.append(pd.read_excel(input_data_path), ignore_index=True)

    # delete unneeded cols 
    df = df.drop('Unnamed: 0', 1)
    df = df.drop('Unnamed: 0.1', 1)
    
    # change names 
    df = df.rename(columns={'Begin':'StartDate', 'End':'EndDate'})
    
    # remove zero time from date cols # TODO: There is likely a better way to do this 
    df['StartDate'] = [str(d).rstrip('0:') for d in df['StartDate']]
    df['EndDate'] = [str(d).rstrip('0:') for d in df['EndDate']]
    
    # adjust when col 
    df = adjust_when(df) 
    
    print(df) 

if __name__ == '__main__': 
    main() 
