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
  Provides utility functions that support the full workflow, such as:
  - Create new test cases from a base case
  - Update OpenFOAM dictionary files with parameter values
  - Submit jobs locally or remotely (via Slurm on HPC systems)
  - Monitor job status in the queue
  - Handle file transfers, compression, and decompression

Assumptions:
  - Called by higher-level scripts (e.g. generate_data.py)
  - Assumes OpenFOAM v2412 dictionary structure when updating
  - Passwordless SSH is configured for HPC submission

Authors
    Simon A. Rodriguez, University College Dublin (UCD). All rights reserved
    Petar Cosic, University College Dublin (UCD). All rights reserved
    Tom Flint, University of Manchester (UOM). All rights reserved
    Philip Cardiff, University College Dublin (UCD). All rights reserved
    
'''


import os
# import functions
# from functions import *
import input_data
from input_data import *
import re

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from joblib import dump, load
import numpy as np
import random

import subprocess
import re
import time
import importlib


def terminal(command):
    os.system(command)
    

def create_test_case(base_case_name, test_case_number):
    name_new_folder = MESH_DENSITY + "/test_case_" + str(test_case_number + 1)
    terminal("mkdir -p "  + name_new_folder)
    terminal("cp -r " + base_case_name + "/* " + name_new_folder)
    terminal("cp -r *py " + "./" + name_new_folder)
    
    
def replace_speed(value, test_case_number):
    name_new_folder = MESH_DENSITY + "/test_case_" + str(test_case_number + 1)
    file_name = "./" + name_new_folder + "/constant/timeVsLaserPosition"
    # Read all lines in the file
    with open(file_name, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    if (OPENFOAM_VERSION == "2412"):
        lines[2] = "    ("+ str((1/value) * 600e-6) + \
                   "      (100e-6 700e-6 0)) \n"
        lines[3] = "    ("+ str((1/value) * 600e-6 + 0.001e-6) + \
                   "      (100e-6 700e-6 0)) \n"
    else:
        # To be implemented
        pass
        
    # Write the new lines in the file 
    with open(file_name, 'w', encoding='utf-8') as f:
        f.writelines(lines)
            


def replace_power(value, test_case_number, speed):
    name_new_folder = MESH_DENSITY + "/test_case_" + str(test_case_number + 1)
    file_name = "./" + name_new_folder + "/constant/timeVsLaserPower"
    # Read all lines in the file
    with open(file_name, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    if (OPENFOAM_VERSION == "2412"):
        lines[1] = "    (0            "+ str(value) + ")\n "
        lines[2] = "    ("+ str(1/(speed) * 600e-6) + "         "+ \
                   str(value) + ") \n"
        lines[3] = "    ("+ str(1/(speed) * 600e-6 + 0.001e-6) + \
                   "         "+ "0) \n"
    else:
        # To be implemented
        pass
        
    # Write the new lines in the file 
    with open(file_name, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def update_openfoam_variable(file_path, full_key, new_value):
    key_parts = full_key.split('.')
    key = key_parts[-1]
    block_path = key_parts[:-1]

    with open(file_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    current_blocks = []
    pending_block_name = None
    inside_target_block = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Open line block: e.g. "metalProperties {"
        match_inline_block = re.match(r'^(\w+)\s*\{$', stripped)
        if match_inline_block:
            block_name = match_inline_block.group(1)
            current_blocks.append(block_name)
            inside_target_block = (current_blocks == block_path)
            new_lines.append(line)
            continue

        # Open two line blocks
        if re.match(r'^\w+$', stripped):
            pending_block_name = stripped
            new_lines.append(line)
            continue
        elif stripped == '{' and pending_block_name:
            current_blocks.append(pending_block_name)
            inside_target_block = (current_blocks == block_path)
            new_lines.append(line)
            pending_block_name = None
            continue

        # Close the blocks
        if stripped == '}':
            if current_blocks:
                current_blocks.pop()
                inside_target_block = (current_blocks == block_path)
            new_lines.append(line)
            continue

        # Detect if we are within the correct block or out of any block
        # in_scope = (current_blocks == block_path) if block_path else (len(current_blocks) == 0)
        in_scope = (
                    (current_blocks == block_path)
                    if block_path
                    else (len(current_blocks) == 0)
                    )

        # Case 1: Double key + dimensions (e.g. "cpL cpL [dims] valor;")
        pattern_dims = rf'^(\s*{key}\s+{key}\s+\[[^\]]+\]\s+)([^\s;]+)(\s*;.*)$'
        match_dims = re.match(pattern_dims, line)
        if in_scope and match_dims:
            prefix, _, suffix = match_dims.groups()
            new_line = f"{prefix}{new_value}{suffix}\n"
            new_lines.append(new_line)
            continue

        # Case 2: Unique key + dimensions (e.g. "rhoG [dims] valor;")
        pattern_simple_dims = rf'^(\s*{key}\s+\[[^\]]+\]\s+)([^\s;]+)(\s*;.*)$'
        match_simple_dims = re.match(pattern_simple_dims, line)
        if in_scope and match_simple_dims:
            prefix, _, suffix = match_simple_dims.groups()
            new_line = f"{prefix}{new_value}{suffix}\n"
            new_lines.append(new_line)
            continue

        # Caso 3: clave sin dimensiones (e.g. "ray_tracing_on false;")
        pattern_nodims = rf'^(\s*{key}\s+)([^\s;]+)(\s*;.*)$'
        match_nodims = re.match(pattern_nodims, line)
        if in_scope and match_nodims:
            prefix, _, suffix = match_nodims.groups()
            new_line = f"{prefix}{new_value}{suffix}\n"
            new_lines.append(new_line)
            continue

        # If it does no coincide with anything, maintain the original line
        new_lines.append(line)

    with open(file_path, 'w') as f:
        f.writelines(new_lines)

    print(f"✅ '{full_key}' updated to {new_value}")


def set_environment_variables():   
    variables_import = RUNNING_ON.lower() + "_inp" 
    imported = importlib.import_module(variables_import)
    hostname = imported.hostname
    run_address = imported.run_address
    OF_LOCATION = imported.OF_LOCATION
    
    
    return hostname, run_address, OF_LOCATION


def set_base_case_name():
    BASE_CASE_NAME = ""
    if (OPENFOAM_VERSION == "2412"):
        BASE_CASE_NAME = MESH_DENSITY + "/base_case_of2412"
    else:
        BASE_CASE_NAME = MESH_DENSITY + "base_case_fe40"
        
    return BASE_CASE_NAME

def create_NN(n_nodes, n_input_variables, n_output_variables):
    # Set the neural network up
    model = Sequential()
    model.add(Dense(units = n_nodes, 
                    kernel_initializer = 'he_normal', 
                    activation = 'relu', input_shape = (None, 
                                                        n_input_variables)))
    model.add(Dense(units = n_output_variables, kernel_initializer = 'he_normal', 
                    activation = 'linear'))
    model.compile(optimizer=Adam(lr = 0.01), loss='mse')
    
    return model
            

def create_scalers():
    x_scaler =  MinMaxScaler()
    y_scaler  =  MinMaxScaler()
    
    return x_scaler, y_scaler

def fit_scalers(x_scaler, y_scaler, input_data, output_data):
    x_scaler.fit(input_data.reshape([input_data.shape[0], input_data.shape[2]])) 
    y_scaler.fit(output_data.reshape([output_data.shape[0], output_data.shape[2]]))
    
def scale_data(x_scaler, y_scaler, input_data, output_data):
    input_data_scaled = x_scaler.transform(input_data.reshape([input_data.shape[0], input_data.shape[2]])) 
    output_data_scaled = y_scaler.transform(output_data.reshape([output_data.shape[0], output_data.shape[2]]))
    
    return input_data_scaled, output_data_scaled

def create_width_depth_height_to_flat_data(good_simulation_cases):
    # Assemble the training set
    width_data = []
    depth_data = []
    height_to_flat_data = []
    cases_ran_properly_and_have_continuous_meltpool = []
    for i in good_simulation_cases:
        name_new_folder = MESH_DENSITY + "/test_case_" + str(i)
        meltpool_i_is_cotinuous = load("./" + name_new_folder + "/continuous.joblib")
        if (meltpool_i_is_cotinuous):
            width_data.append(load("./" + name_new_folder + "/width.joblib"))
            depth_data.append(load("./" + name_new_folder + "/depth.joblib"))
            height_to_flat_data.append(load("./" + name_new_folder + "/height_to_flat.joblib"))
            cases_ran_properly_and_have_continuous_meltpool.append(i)


    width_data = np.array(width_data)
    depth_data = np.array(depth_data)
    height_to_flat_data = np.array(height_to_flat_data)
    cases_ran_properly_and_have_continuous_meltpool = np.array(cases_ran_properly_and_have_continuous_meltpool)
    return width_data, depth_data, height_to_flat_data, \
           cases_ran_properly_and_have_continuous_meltpool

def seed_everything(SEED):
    random.seed(SEED)
    np.random.seed(SEED)
    tf.random.set_seed(SEED)
    
def create_input_data_and_output_data(width_data, depth_data, 
                                      height_to_flat_data, number_useful_cases,
                               cases_ran_properly_and_have_continuous_meltpool,
                                      parameters):
    # # Create the data for the NN
    width_data = width_data.reshape((number_useful_cases, 1, 1))
    depth_data = depth_data.reshape((number_useful_cases, 1, 1))
    height_to_flat_data = height_to_flat_data.reshape((number_useful_cases, 1, 1))

    parameters_valid_cases = parameters[cases_ran_properly_and_have_continuous_meltpool-1]
    input_data = parameters_valid_cases.reshape((number_useful_cases, 1, 
                                                 parameters_valid_cases.shape[1]))
    output_data = np.concatenate((width_data, depth_data, height_to_flat_data), 
                                 axis = 2)
    
    return input_data, output_data, parameters_valid_cases
    

def create_simulation_cases(number_cases, base_case_name, parameters):
    # Create the simulation cases
    for i in range(number_cases):    
        name_new_folder = MESH_DENSITY + "/test_case_" + str(i + 1)
        # Create the test cases
        create_test_case(base_case_name, i)
        
        #Replace the correct values for radius,
        update_openfoam_variable("./" + name_new_folder + 
                                  "/constant/laserProperties", "laserRadius", 
                                  parameters[i, 2]/2)
    
        #Replace the correct values for scanning speed
        replace_speed(parameters[i, 0], i)
    
        #Replace the correct values for power
        replace_power(parameters[i, 1], i, parameters[i, 0])
        # To replace a variable in the constant/laserProperties file, this is the 
        # sample:
        # update_openfoam_variable("./" + name_new_folder + "/constant/laserProperties", "ray_tracing_on", "true")
        # To replace a variable in the constant/thermalProperties file,these are the 
        # samples:
        # update_openfoam_variable("./" + name_new_folder + "/constant/thermalProperties", "metalProperties.cpL", "800")
        # update_openfoam_variable("./" + name_new_folder + "/constant/thermalProperties", "TRef", "300")
        # To replace a variable in the constant/transportProperties file,these are the 
        # samples:
        # update_openfoam_variable("./" + name_new_folder + "/constant/transportProperties", "material.rhoS", "800")
        # update_openfoam_variable("./" + name_new_folder + "/constant/transportProperties", "STgrad", "300")    
        
        # Note there are particular functions for replacing the speed and power


    
def submit_remote_job(remote_host, remote_case_path, local_case_path):
    # Submit job on HPC via SSH
    # cmd = f'ssh {remote_host} "cd {remote_case_path} && sbatch singleTracksonic.sh"'
    cmd = "ssh " + remote_host + ' "cd ' + remote_case_path + " && sbatch singleTrack" + RUNNING_ON + '.sh"'
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
    
    # Extract job ID from output
    match = re.search(r"Submitted batch job (\d+)", result.stdout)
    if match:
        job_id = match.group(1)
        # Save job ID locally inside case folder
        with open(os.path.join(local_case_path, "job_id.txt"), "w") as f:
            f.write(job_id)
        print(f"✅ Submitted case {local_case_path}, job ID: {job_id}")
        return job_id
    else:
        print(f"❌ Could not extract job ID for {local_case_path}")
        return None
    
    
def is_job_in_queue(job_id, hpc_host="sonicstaff"):
    cmd = f'ssh {hpc_host} "squeue -j {job_id}"'
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
    return str(job_id) in result.stdout

def monitor_job_is_running(id_current_job, hostname):
    is_current_job_in_queue = True
    while (is_current_job_in_queue):
        is_current_job_in_queue = is_job_in_queue(id_current_job, hostname)
        if (is_current_job_in_queue):
            print("Job ", str(id_current_job), " is still in the queue")
            time.sleep(STATUS_CHECK_FREQUENCY_IN_MIN * 60)  # Sleep for X minutes
        else:
            print("Job ", str(id_current_job), " is finished")
        
    
    
