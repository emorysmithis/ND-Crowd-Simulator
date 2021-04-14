#!/usr/bin/env python 

import sys 
import pandas as pd
import os
import re 

def usage(exitcode=0): 
    progname = os.path.basename(sys.argv[0])
    print(f'''Usage: {progname} -d data_file.xlsx -o output_data.xlsx -b building_name.xlsx []
    -d input_data_path      Data file to use as base 
    -o output_data_path     Output data file
    -b buildings_data path  List of buildings names from osmnx''')
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

def adjust_where(df, bdf):
    # remove edge cases 
    df['Where'] = df['Where'].str.replace('\d+', '') # TODO: FutureWarning
    df['Where'] = df['Where'].str.replace('ALTERNATING ATTEND ', '')
    df['Where'] = df['Where'].str.replace(' ALTERNATING ATTEND', '')
    df['Where'] = df['Where'].str.replace('ONLINE COURSE ', '')
    df['Where'] = df['Where'].str.replace(' ONLINE COURSE', '')
    for index,row in df.iterrows(): 
        df.loc[index, 'Where'] = adjust_building(df.loc[index, 'Where'], bdf)
    return df 

def adjust_building(where, bdf): 
    # remove repeating phrases and single letters 
    words = [] 
    for word in where.split(): 
        if word not in words and len(word) > 1: 
            words.append(word)
    new_building = " ".join(words)
    # adjust building names to match osmnx 
    if 'Jenkins' in new_building: 
        new_building = 'Jenkins-Nonovic Hall'
    elif 'Stayer' in new_building: 
        new_building = 'Stayer Center for Executive Education'
    elif 'Performing' in new_building: 
        new_building = 'DeBartolo Performing Arts Center'
    elif 'Eck ND Visitors' in new_building: 
        new_building = 'Eck Visitors Center'
    elif 'Hayes' in new_building: 
        new_building = 'Hayes-Healy Center'
    elif 'Walsh Hall of Architecture' in new_building: 
        new_building = 'Walsh Family Hall of Architecture'
    elif 'Stinson' in new_building: 
        new_building = 'Stinson-Remick Hall'
    elif 'Snite' in new_building: 
        new_building = 'Snite Museum'
    elif 'Hesburgh Ctr.' in new_building: 
        new_building = 'Hesburgh Center for International Studies'
    elif 'Duncan Student Center' in new_building: 
        new_building = 'Duncan Student Center'
    elif 'Ricci' in new_building: 
        new_building = 'Ricci Band Rehearsal Hall'
    elif 'Eck Hall of Law' in new_building or 'Biolchini' in new_building: 
        new_building = 'Law School'
    elif 'Joyce' in new_building: 
        new_building = 'Joyce Athletic Center'
    elif 'Morris Inn' in new_building: 
        new_building = 'Morris Inn'
    elif 'Geddes' in new_building: 
        new_building = 'Geddes Hall'
    elif 'Corbett' in new_building: 
        new_building = 'Corbett Family Hall'
    elif 'Mendoza' in new_building: 
        new_building = 'Mendoza College of Business'
    elif 'West Lake' in new_building: 
        new_building = 'West Lake Hall'
    elif 'Pasquerilla Center' in new_building: 
        new_building = 'Pasquerilla Center'
    elif "O'Neill Hall of Music" in new_building: 
        new_building = "O'Neill Hall" 
    elif 'DEPARTMENTAL' in new_building or 'TBA' in new_building or 'ONLINE' in new_building: 
        new_building = 'DORM'
    elif 'Innovation' in new_building: 
        new_building = 'Compton Family Ice Arena'
    if bdf['Name'].str.contains(new_building).any(): 
        pass
    elif new_building != 'DORM':
        print(f"{new_building}| not found")  
    return new_building 

def create_buildings_df(buildings_data_path): 
    # create data frame 
    bdf = pd.DataFrame() 
    bdf = bdf.append(pd.read_excel(buildings_data_path), ignore_index=True)
    # delete unneeded cols 
    bdf = bdf.drop('Unnamed: 0', 1)
    print(bdf.columns)
    # change names 
    bdf = bdf.rename(columns={0:'Name'})
    return bdf 

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
    if len(arguments) < 6: 
        usage(0)
    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-d':
            input_data_path = arguments.pop(0)
        elif argument == '-o':
            output_data_path = arguments.pop(0)
        elif argument == '-b': 
            buildings_data_path = arguments.pop(0)
        elif argument == '-h':
            usage(0)
        else:
            usage(1)
    
    # ensure input data file exists 
    if not os.path.exists(input_data_path) or not os.path.exists(buildings_data_path):
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
    
    # create buildings data path 
    bdf = create_buildings_df(buildings_data_path)

    # adjust where col 
    df = adjust_where(df, bdf)

    #print(df)
    df.to_excel(output_data_path)

if __name__ == '__main__': 
    main() 
