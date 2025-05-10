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

csv_file = "meltpool.csv"
df = pd.read_csv(csv_file)
x_coords = df["Points:0"]
z_coords = df["Points:2"]



width = x_coords.max() - x_coords.min()
depth = z_coords.max() - z_coords.min()

print(f"Meltpool Depth: {depth:.2e} m")
print(f"Meltpool Width: {width:.2e} m")


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

print(f"height_to_flat Width: {height_to_flat:.2e} m")


