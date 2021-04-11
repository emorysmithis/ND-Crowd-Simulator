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

def parse_sections(orig, index, df): 
    sections = orig.split('(')
    dup = df.loc[index]
    for i,section in enumerate(sections[1:]): 
        if i == 0: 
            df.loc[index, 'When'] = section[3:]
            df.loc[index, 'Days'] = get_days(section[3:])
            df.loc[index, 'Start Time'] = get_times(section[3:])[0]
            df.loc[index, 'End Time'] = get_times(section[3:])[1]

            
        else: 
            dup['When'] = section[3:]
            try: # TODO: these following 3 lines cause warnings 
                dup['Days'] = get_days(section[3:])[0]
                dup['Start Time'] = get_times(section[3:])[0]
                dup['End Time'] = get_times(section[3:])[1]

            except: # ignore cases where there are no days 
                pass
            df = df.append(dup, ignore_index=True)
    return df 

def adjust_where(df): 
    df['Where'] = df['Where'].str.replace('\d+', '') # TODO: FutureWarning 
    return df

def adjust_when(df):  
    # add a day column 
    df['Days'] = ""
    df['Start Time'] = ""
    df['End Time'] = ""
    for index,row in df.iterrows():
        if row['When'][0:3] != "TBA":
            orig = row['When']
            # account for When with sections 
            regex1 = r'\('
            section_rows = re.findall(regex1, orig)
            if len(section_rows) > 0:
                df = parse_sections(orig, index, df)
            else: 
                df.loc[index, 'Days'] = get_days(orig)
                df.loc[index, 'Start Time'] = get_times(orig)[0]
                df.loc[index, 'End Time'] = get_times(orig)[1]
    return df 

def get_times(orig): 
    noSpaces = orig.replace(" ", "")
    regex = r'([0-9]+:[0-9]+[AP])-([0-9]+:[0-9]+[AP])'
    times = re.search(regex, noSpaces)
    if len(times.groups()) != 2: 
        print("ERROR, When does not include 2 times")
    else: 
        start,end = times.groups()
        start = convert24(start)
        end = convert24(end)
    return (start,end)

def convert24(time): 
    regex = r'([0-9]+):([0-9]+)[AP]'
    hourMin = re.search(regex, time)
    hours,mins = hourMin.groups() 
    if time[-1] == 'P' and int(hours) != 12: 
        hours = str(int(hours) + 12)  
    return (f"{hours}:{mins}")

def get_days(orig): 
    noSpaces = orig.replace(" ", "")
    regex = r'([A-Z]+)-.*'  # get the days from the When col 
    days = re.findall(regex,noSpaces)
    return days 


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
    
    # adjust where col 
    df = adjust_where(df)

    #print(df)
    df.to_excel(output_data_path)

if __name__ == '__main__': 
    main() 
