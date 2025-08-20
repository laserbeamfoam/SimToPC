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
  Script for calculating geometric quantities from the meltpool.

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
# import functions_meltpool_geometry
# from functions_meltpool_geometry import *
import functions
from functions import (is_meltpool_continuous, 
                       calculate_geometry_middle_sections,
                       calculate_geometry_full_meltpool)


print("Checking if the meltpool is continuous")
continuous = is_meltpool_continuous("y_z_slice_meltpool.csv")
print("Meltpool is continuous: ", continuous)


if (continuous):
    print("Calculate geometric quantities at the central section")
    calculate_geometry_middle_sections(CSV_XZ = "x_z_slice_meltpool.csv")

    print("Calculate geometric quantities at the whole meltpool")
    calculate_geometry_full_meltpool(CSV_3D = "meltpool.csv")