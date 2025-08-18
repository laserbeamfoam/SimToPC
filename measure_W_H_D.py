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
    

Purpose:
  Postprocessing script for finished simulation cases:
  - Uses ParaView (pvpython) to extract melt pool metrics
  - Computes W (width), H (depth), and D (height-to-max-width ratio)
  - Checks track continuity (boolean output)
  - Provides both mid-plane values and statistical measures along the track

Assumptions:
  - ParaView (with pvpython) is installed and accessible in PATH
  - Simulation results exist in "test_case_i" folders created
    by generate_data.py
  - Case outputs are consistent with laserMeltFoam (OpenFOAM v2412)

Method:
  1. Mid-plane evaluation:
     - W, H, and D are measured at the middle section of the domain
       (y = 400 microns).
  2. Track-averaged evaluation:
     - The first and last regions equal to one laser spot diameter
       are excluded to remove entrance/exit effects.
     - On the remaining melt pool, W, H, and D are calculated for
       all y positions.
     - Final outputs include the mean and standard deviation of W, H, and D
       along the trimmed melt pool.
  3. Continuity check:
     - At x = 100 microns, verifies that material is present at all
       y-locations of the melt pool cross-section.
     - Result is saved as a boolean ("continuous.joblib").

Outputs:
  - For each "test_case_i" folder:
      W.joblib          → melt pool width metrics
      H.joblib          → melt pool depth metrics
      D.joblib          → melt pool height-to-max-width metrics
      continuous.joblib → boolean: track continuity
  - Image folders:
      images_full_meltpool → ParaView clips/slices for the whole melt pool
      images_x_z_slice     → ParaView outputs for x–z slice (y = 400 µm)
      images_y_z_slice     → ParaView outputs for y–z slice (x = 100 µm)

Authors
    Simon A. Rodriguez, University College Dublin (UCD)
    Petar Cosic, University College Dublin (UCD)
    Tom Flint, University of Manchester
    Philip Cardiff, University College Dublin (UCD)

'''

from functions import (set_environment_variables, terminal, 
                       is_meltpool_continuous, 
                       calculate_geometry_middle_sections,
                       calculate_geometry_full_meltpool) 
import numpy as np
import input_data
from input_data import *


# source the correct OpenFOAM, based on the system and OF version
hostname, run_address, OF_LOCATION = set_environment_variables()

# Read the operational parameters
parameters = np.loadtxt("./parameters.txt", skiprows=1)

# Count the total number of cases
number_cases = parameters.shape[0]

# Calculate results (width, depth, etc)
for i in range(number_cases):
    name_new_folder = MESH_DENSITY + "/test_case_" + str(i + 1)
    print("\n Measuring geometry-based quantities for test_case_" + str(i + 1))
    terminal(f'cp extract* {name_new_folder}/')
    terminal(f'cp quantities_from_meltpool.py {name_new_folder}/')
    terminal(f'cp functions.py {name_new_folder}/')
    terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && pvpython extract_meltpool.py"')
    terminal(f'cd {name_new_folder} && mkdir images_full_meltpool && mv *png images_full_meltpool/')
    terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && pvpython extract_x_z_slice_meltpool.py"')
    terminal(f'cd {name_new_folder} && mkdir images_x_z_slice && mv *png images_x_z_slice/')
    terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && pvpython extract_y_z_slice_meltpool.py"')
    terminal(f'cd {name_new_folder} && mkdir images_y_z_slice && mv *png images_y_z_slice/')
    terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && python quantities_from_meltpool.py"')
    print("\n Finished measuring geometry-based quantities for test_case_"+ str(i + 1), "\n")

print("Geometry measurement finished.")