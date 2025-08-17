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
    This script automates the generation, execution, and retrieval of 
    OpenFOAM-based simulations for melt pool analysis. It further trains a 
    neural network surrogate model on the simulation results to predict 
    melt pool characteristics (width, depth, height-to-flat) based on input 
    parameters.

Authors
    Simon A. Rodriguez, University College Dublin (UCD). All rights reserved
    Petar Cosic, University College Dublin (UCD). All rights reserved
    Tom Flint, University of Manchester. All rights reserved
    Philip Cardiff, University College Dublin (UCD). All rights reserved

Assumptions:
    - The base case is correctly configured and mesh is generated.
    - When using laserMeltFoam, setSolidFraction has already been run locally
    - decomposePar has been run locally
    - Passwordless SSH access to the remote server is available.
    - Required tools (OpenFOAM, pvpython, TensorFlow, etc.) are installed and 
    sourced properly.
'''

from functions import set_environment_variables, terminal
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
    terminal(f'cp extract* {name_new_folder}/')
    terminal(f'cp quantities_from_meltpool.py {name_new_folder}/')
    terminal(f'cp functions_meltpool_geometry.py {name_new_folder}/')
    terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && pvpython extract_meltpool.py"')
    terminal(f'cd {name_new_folder} && mkdir images_full_meltpool && mv *png images_full_meltpool/')
    terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && pvpython extract_x_z_slice_meltpool.py"')
    terminal(f'cd {name_new_folder} && mkdir images_x_z_slice && mv *png images_x_z_slice/')
    terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && pvpython extract_y_z_slice_meltpool.py"')
    terminal(f'cd {name_new_folder} && mkdir images_y_z_slice && mv *png images_y_z_slice/')
    terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && python quantities_from_meltpool.py"')

print("Geometry measurement finished.")