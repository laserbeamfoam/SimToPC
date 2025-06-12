'''
License
  This program is free software: you can redistribute it and/or modify 
  it under the terms of the GNU General Public License as published 
  by the Free Software Foundation, either version 3 of the License, 
  or (at your option) any later version.

  This program is distributed in the hope that it will be useful, 
  but WITHOUT ANY WARRANTY; without even the implied warranty of 
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 

  See the GNU General Public License for more details. You should have 
  received a copy of the GNU General Public License along with this 
  program. If not, see <https://www.gnu.org/licenses/>. 

Description
  Script for calculating geometric quantities from the meltpool extracted
  via postproc2.py.

Authors
    Simon A. Rodriguez, University College Dublin (UCD). All rights reserved
    Petar Cosic, University College Dublin (UCD). All rights reserved
    Tom Flint, University of Manchester. All rights reserved
    Philip Cardiff, University College Dublin (UCD). All rights reserved
    
'''

import pandas as pd
import numpy as np
import input_data
from input_data import *
from joblib import dump, load


print("Checking if the meltpool is continuous")
# Check continuity
csv_file = "meltpool_forcontinuity.csv"
df = pd.read_csv(csv_file)

# Filtra las filas donde Points_1 (es decir, y) está DENTRO del rango
y_inf_limit = 100e-6 + LASER_SPOT_SIZE/2
y_sup_limit = 700e-6 - LASER_SPOT_SIZE/2
df = df[(df["Points_1"] >= y_inf_limit) & (df["Points_1"] <= y_sup_limit)]

x_coords = df["Points_0"]
y_coords = df["Points_1"]
z_coords = df["Points_2"]

continuous = True
 
# Remove the beginning/end effect





# Sort unique Z-values from top to bottom
unique_x = np.sort(x_coords.unique())[::-1]
unique_y = np.sort(y_coords.unique())[::-1]


min_unique_y = min(unique_y)
max_unique_y = max(unique_y)

sorted_unique_y = np.sort(unique_y)
# step = CELL_SIZE
y_point = min_unique_y
meltpool_is_continuos = True

if ( (max(abs(np.diff(sorted_unique_y))) - CELL_SIZE) > 1e-8 ):
    continuous = False 
    

dump(continuous, "./continuous.joblib")


if (continuous):

    csv_file = "meltpool_forwidth.csv"
    df = pd.read_csv(csv_file)
    x_coords = df["Points_0"]
    y_coords = df["Points_1"]
    z_coords = df["Points_2"]
    
    
    
    width = x_coords.max() - x_coords.min()
    depth = z_coords.max() - z_coords.min()
    
    print(f"Meltpool Depth: {depth:.2e} m")
    print(f"Meltpool Width: {width:.2e} m")
    
    print("Saving width")
    dump(width, "./width.joblib")
    
    print("Saving depth")
    dump(depth, "./depth.joblib")
    
    # Sort unique Z-values from top to bottom
    unique_z = np.sort(z_coords.unique())[::-1]
    
    prev_count = 0
    contact_z = None
    
    for i, z_val in enumerate(unique_z):
        count = (z_coords == z_val).sum()
    
        if count < prev_count and i > 0:
            contact_z = unique_z[i - 1]  # The previous Z was the widest
            break
    
        prev_count = count
    
    if contact_z is None:
        raise ValueError("Could not determine contact zone: width may not decrease.")
    
    # Measure width at the contact_z level
    x_at_contact = x_coords[z_coords == contact_z]
    width = x_at_contact.max() - x_at_contact.min()
    
    
    height_to_flat = contact_z - z_coords.min()
    
    print("Saving height_to_flat")
    dump(height_to_flat, "./height_to_flat.joblib")
    
    
    
