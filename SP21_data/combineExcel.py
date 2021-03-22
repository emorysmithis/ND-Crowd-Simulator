import os 
import pandas as pd 
cwd = os.path.abspath('') 
files = os.listdir(cwd) 

df = pd.DataFrame()
for file in files: 
    if file.endswith('.xlsx'):
        print(f"Trying to add {file}")
        try: 
            df = df.append(pd.read_excel(file), ignore_index=True) 
            print(f"Added {file}") 
        except: 
            print(f"Couldn't add {file}") 
df.head() 
df.to_excel('ALL_SP21_COURSES.xlsx') 

