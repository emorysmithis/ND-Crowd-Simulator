import sys 
import pandas as pd 

# get input file 
args = sys.argv
inputfile = args[1]
print(f"input file: {inputfile}") 

# create data frame from input file 
df = pd.DataFrame() 
df = df.append(pd.read_excel(args[1]), ignore_index=True)

# remove complete duplicates 
df.drop_duplicates(keep='first', inplace=True) 
df.to_excel(f"noCompleteDups_{inputfile}") 

# if we wanted to remove duplicate classes (might not want to because removing seats) 
# df.drop_duplicates(subset=['When', 'Instructor'], keep='first', inplace=True)
# df.to_excel(f"noDup_{inputfile}") 


# remove all courses Where = TBA || ONLINE 
df.drop(df.index[df['Where'] == 'TBA'], inplace=True)
df.to_excel(f"noTBA_{inputfile}") 
df.drop(df.index[df['Where'] == 'ONLINE COURSE'], inplace=True)
df.to_excel(f"noTABnoONLINE_{inputfile}") 
