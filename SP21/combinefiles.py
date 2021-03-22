import os
import pandas as pd
cwd = os.path.abspath('')
files = os.listdir(cwd)

## Method 1 gets the first sheet of a given file
df = pd.DataFrame()
for file in files:
    if file.endswith('.xlsx'):
        df = df.append(pd.read_excel(file), ignore_index=True)
df.head()
df.to_excel('SP21.xlsx')