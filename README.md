# ND-Crowd-Simulator 
## Branches 
- main: this branch contains the scripts you would need to reproduce our project and some of the files that you would make along the way 
- data: this branch contains the files and scripts needed for data collection and processing 
- simulation: this branch contains the files and scripts needed to run our simulations and visualize the results
- mapping: this branch contains the scripts used to create the list of building names that osm accepts as valid buildings for Notre Dame, IN 

## Files 
### Data 
- `12_students` ... `12000_students` directories: these directories contain the output files from `simple_setup.py`. These output files are JSON files, one for each weekday. They also contain `time.txt` files which have the earliest class time minus 30 minutes and the last class time. This `time.txt` file is used in our `automate.py` script. 
- `SP21 directory`: this directory contains all of the data downloaded from the ND class search website. They are in .xlsx format instead of the original .xls format because .xls is deprecated in many python packages.
    - `combineExcel.py`: this script aggregates all of the .xlsx files in the current working directory 
- `SP21_data directory`: this directory contains the same files as SP21 directory plus the aggregated .xlsx file with all of the courses in it. 
- `cleanedData` directory: this directory contains the output excel files from `cleanData.py`
- `simData` directory: this directory contains the `createSimData.py` script and the necessary inputs and the outputs for this script 
    - `createSimData.py` takes in the aggregated courses file and the building names file as its inputs and outputs a cleaned version of the courses file with the building names changed to buildings that are accepted by osm
- `stats` directory: this directory contains stats.py and the necessary input and output for this script. 
    - `stats.py` takes in the aggregated courses file and outputs how many classes, how many seats are taken, and the average number of classes for undergraduate and graduate students 
- `ALL_SP21_COURSES.xlsx`: this file is the aggregated courses information from the class search website 
- `class_search.xlsx`: this files is the output of createSimData.py and it is the file that is the input to simple_setup.py. It is the cleaned, aggregated course information that contains the correct building names, start time, end time, and days columns. It also has all of the classes open. 
- `cleanData.py`: this script removes the duplicates from the aggregated course file and outputs files where either no classes are deletd, the TBA classes are deleted or the TBA and ONLINE courses are deleted 
- `dorms.xlsx`: this file contains the list of dorm names accepted by osm 
- `simple_setup.py`: this script takes in the `class_search.xlsx` and the `dorms.xlsx`. It outputs the JSON files for Monday-Friday which contain the journeys for every student on that day. 
### Simulation 
- `output_xlsx` directory: this directory contains the output files from `parse_output.py`. These excel files contain the same information that the output files from the simulations contain. However, all of those numbers for the different populations and conditions can be seen in one place here. Note: the files contain information for the population in the filename as well as the information for the populations smaller than the population in the file name. For example `120_paths_batch.xlsx` contains information from the 120, 60, and 12 student population simulations. The files without a population name contain the information for all of the population sizes. 
    - `default` and `default_parallel`: default simulation on the cloud 
    - `local`: default simulation locally 
    - `paths` and `paths_parallel`: n-shortest path simulations in parallel on the cloud 
    - `paths_batch`: n-shortest path simulations in parallel, started in batches, cloud 
    - `speeds_batch`: transportation simulations in parallel, started in batches, cloud 
- `overall_time_outputs`: this directory contains the overall runtimes for the simulations. For example paths_batch_12_time.txt contains how long it took to run all of the path simulations in parallel, started in batches, on the cloud. 
- `visualizations` directory: this directory contains .png files which are the output of our `visualize.py` script 
- `automate.py`: this script takes in journey JSON files. This script starts the default simulations in parallel 
- `automate_paths.py`: this takes in journey JSON files. This script starts the n-shortest path simulations in parallel (batch)  
- `automate_speeds.py`: this script takes in journey JSON files. This script starts the transportation simulations in parallel (batch) 
- `parse_output.py`: this scripts looks at all of the output files from the simulations and aggregates that information into an excel file 
- `sequential.py`: this takes in weekday journey JSON files. This script can start simulations that run sequentially 
- `simulation.py`: this script takes in one of the weekday journey JSON files and outputs the 50 edges/sidewalks with the greatest number of people and how long the simulation took to run 
- `visualize.py`: this script takes in an output file from simulation.py and outputs a picture of the ND campus with sidewalks colored to indicate how many people are on them (red = more people, blue = less peopel, purple = middle) 

## How to Run
### Requirements 
- python3 
### Data Collection, Data Processing, and Setup 
1. Go to Class Search: https://class-search-secure.nd.edu/reg/srch/SecureClassSearchServlet
2. For each subject, in SP21 on Main Campus, download Excel 
3. Manually convert .xls to .xlsx 
4. Use `combineExcel.py` to combine all of the attribute .xlsx files into one aggregated course file 
    - `python3 combineExcel.py` 
    - make sure to delete previously aggregated file
    - output: `ALL_SP21_COURSES.xlsx` 
5. Use `cleanData.py` to clean up this aggregated course file 
    - `python3 cleanData.py ALL_SP21_COURSES.xlsx` 
    - output: 3 xlsx files: 
        - `noCompleteDups_ALL_SP21_COURSES.xlsx`: no duplicate classes 
        - `noTBA_ALL_SP21_COURSES.xlsx` : no duplicate classes and no classes where time or location is TBA 
        - `noTABnoONLINE_ALL_SP21_COURSES.xlsx`: no duplicate classes and no classes where time or location is TBA or ONLINE 
6. Use  `createSimData.py` to create class_search.xlsx, an excel file that is better suited for the `simple_setup.py` script 
    - `./createSimData.py -d noCompleteDups_ALL_SP21_COURSES.xlsx -o class_search.xlsx -b building_names.xlsx` 
    - output: class_search.xlsx
    - `building_names.xlsx` is an input to this script, but an output from the `createBuildingsList.py` script in the mapping branch 
7. Use `simple_setup.py` to create the journey JSON files 
    - `./simple_setup.py -c class_search.xlsx -d dorms.xlsx -ugrads 8000 -grads 4000 -dir 12000_students` 
        - you have to run this script for each population size 
        - dorms.xlsx is a modified version of building_names.xlsx that only contains dorm names (we created this file manually) 
        - the `-ugrads` and `-grads` flags say how many of each type of student we want to create setup files for 
        - the `-dir` flag says where we want to save the output JSON files to 
        - output: 
            - `12000_students/m_students.txt`: journey JSON file for Monday
            - `12000_students/t_students.txt`: journey JSON file for Tuesday 
            - `12000_students/w_students.txt`: journey JSON file for Wednesday
            - `12000_students/r_students.txt`: journey JSON file for Thursday 
            - `12000_students/f_students.txt`: journey JSON file for Friday 
            - `12000_students/time.txt`: text file containing start and end time of simulation based on first and last class time 



### Automation/Simulation 
