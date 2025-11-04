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
  Main driver script for generating and running simulation cases:
  - Reads parameter sets from parameters.txt
  - Creates new case folders from a base case
  - Applies laser power, speed, and radius values
  - Runs simulations locally or submits them to an HPC
  - Retrieves, compresses, and unpacks simulation results

Assumptions:
  - Passwordless SSH access is configured for HPC systems
  - The solver is laserMeltFoam (see https://github.com/laserbeamfoam/laserMeltFoam)
  - OpenFOAM v2412 is installed and working properly

Outputs:
  - At the end of execution, a folder named "test_case_i" will be created
    for each case listed in parameters.txt (where i is the case index).
    Each "test_case_i" folder contains the corresponding simulation setup
    and results for that evaluated case.


Description
    This script automates the generation, execution, and retrieval of 
    OpenFOAM-based simulations for melt pool analysis. It further trains a 
    neural network surrogate model on the simulation results to predict 
    melt pool characteristics (width, depth, height-to-flat) based on input 
    parameters.

Authors
    Simon A. Rodriguez, University College Dublin (UCD). All rights reserved
    Petar Cosic, University College Dublin (UCD). All rights reserved
    Tom Flint, University of Manchester (UOM). All rights reserved
    Philip Cardiff, University College Dublin (UCD). All rights reserved

'''

from src.functions_generate_data_relate_biot_deff import * 
import numpy as np
import input_data_relate_biot_deff
from input_data_relate_biot_deff import *
from joblib import dump, load
import random
import re

# source the correct OpenFOAM, based on the system and OF version
hostname, run_address, OF_LOCATION = set_environment_variables()

# Select the proper base case
BASE_CASE_NAME = set_base_case_name()

# Read the operational parameters
parameters = np.loadtxt("./parameters_relate_biot_deff.txt", skiprows=1)

# Count the total number of cases
number_cases = parameters.shape[0]

# Count the total number of operational parameters to evaluate
number_of_variables = parameters.shape[1]

# Create the simulation cases, locally        
create_simulation_cases(number_cases, BASE_CASE_NAME, parameters)

# Execute the simulations
if (RUNNING_ON == "LOCAL"):
    for i in range(number_cases):  
        name_new_folder = MESH_DENSITY + "/test_case_" + str(i + 1)
        terminal("cd " + name_new_folder + "/system/ && mv decomposeParDict_16cores decomposeParDict")
        terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && ./Allrun_local"')

else:
    for i in range(number_cases):  
        name_new_folder = MESH_DENSITY + "/test_case_" + str(i + 1)
        # # Prepare the required files
        terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && cp -r initial 0"')      
        terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && blockMesh"')
        terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && setSolidFraction"')
        terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && decomposePar"')
        
        # Transfer the files to the HPC system
        print("Transferring the test case ", str(i+1))
        
        if (i == 0):
            # Create the remote folder that corresponds to MESH_DENSITY
            terminal(f'ssh {hostname} "cd {run_address} && mkdir {MESH_DENSITY}"') 
        
        terminal("scp -r " + name_new_folder +" " + hostname+ ":" + run_address + name_new_folder)
    
        # Submit the job
        id_current_job = submit_remote_job(hostname, 
              f"{run_address}{name_new_folder}", 
              name_new_folder)
        monitor_job_is_running(id_current_job, hostname)
        
        # Some HPC systems, like Meluxina, impose a limit on the number of 
        # files, therefore, in this script, the resulting files are 
        # stored in just ONE .zip file
        # Create a test_case_i.zip file and remove test_case_i folder 
        terminal(f'ssh {hostname} "cd {run_address}{name_new_folder} && cd .. && zip -r test_case_{str(i+1)}.zip test_case_{str(i+1)} && [ -f test_case_{str(i+1)}.zip ] && rm -r test_case_{str(i+1)} && echo "Compression successful and folder deleted.""')
        
        # Pull the results
        terminal("scp -r " + hostname + ":" + run_address + name_new_folder +".zip" + " ./" + MESH_DENSITY + "/")        
        
        # Remove test_case_i.zip
        terminal(f'ssh {hostname} "cd {run_address}{MESH_DENSITY} && rm *.zip "')
        
        # Remove the original test_case_i 
        terminal("rm -r " + name_new_folder)

# Unzip the results
for i in range(number_cases):  
    name_new_folder = MESH_DENSITY + "/test_case_" + str(i + 1)
    terminal("unzip " + name_new_folder + ".zip -d " + MESH_DENSITY + "/")
    terminal("rm " + name_new_folder +".zip")

print("Data generation completed.")