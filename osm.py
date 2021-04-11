#!/usr/bin/env python

import osmnx as ox 
import matplotlib.pyplot as plt
import pandas as p 

place_name = 'Notre Dame, Indiana, United States'
buildings = ox.geometries_from_place(place_name, tags={'building':True})
bnf = 'building_names.xlsx'
buildings_set = set()
for name in buildings['name']:
    if type(name) == str:
        print(name)
        buildings_set.add(name)
buildings_list = list(buildings_set)
buildings_list.sort()
df = p.DataFrame(buildings_list)
df.to_excel(bnf)
