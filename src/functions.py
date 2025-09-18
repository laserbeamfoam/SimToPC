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
import pandas as pd
import random

import subprocess
import re
import time
import importlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


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
    variables_import = "input_files."+ RUNNING_ON.lower() + "_inp" 
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
            width_data.append(load("./" + name_new_folder + "/W.joblib"))
            depth_data.append(load("./" + name_new_folder + "/H.joblib"))
            height_to_flat_data.append(load("./" + name_new_folder + "/D.joblib"))
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
        
def define_good_simulation_cases(MESH_DENSITY, number_cases):
    good_simulation_cases = [] # List of the cases that ran properly
    for i in range(1, number_cases + 1):
        name_new_folder = MESH_DENSITY + "/test_case_" + str(i)
        files_in_folder_i = os.listdir("./" + name_new_folder)
    
        # Verificar si "finished.txt" está en la lista
        if 'finished.txt' in files_in_folder_i:
            good_simulation_cases.append(i)
        #     pass
        # else:
        #     print(name_new_folder + " did not run properly")
        #     print("Check the simulations that failed")
        #     break
    if (len(good_simulation_cases) < number_cases):
        print("Some simulation cases did not run properly.")
    return good_simulation_cases

def generate_x_y_levels_for_predictions(parameters_valid_cases, x_ind, y_ind):
    x_vals = np.linspace(min(parameters_valid_cases[:, x_ind]), 
                         max(parameters_valid_cases[:, x_ind]), 
                         n_divisions_for_prediction)
    y_vals = np.linspace(min(parameters_valid_cases[:, y_ind]), 
                         max(parameters_valid_cases[:, y_ind]), 
                         n_divisions_for_prediction)
    
    return x_vals, y_vals
    

def generate_prediction_map(input_variables_for_map, output_variables_for_map,
                            parameters_valid_cases, x_scaler, y_scaler, model,
                            POSSIBLE_OUTPUTS, x_name, y_name):
    
    for i in range(len(POSSIBLE_OUTPUTS)):
        # Generate the x and y values that will be used in th predicions 
        x_vals, y_vals = generate_x_y_levels_for_predictions(parameters_valid_cases, 
                                                      x_ind=input_variables_for_map[0],
                                                      y_ind=input_variables_for_map[1])
    
        # Generate a grid with x_vals and y_vals
        x, y = np.meshgrid(x_vals, y_vals)
    
    
        # Reshape x and y to make predictions with the NN
        x_for_map = x.reshape((x.shape[0] * x.shape[0], 1, 1))
        y_for_map = y.reshape((y.shape[0] * y.shape[0], 1, 1))
        z_for_map = np.zeros(x_for_map.shape) #This initialises z_for_map
        # Note in this case, there is only 1 Z level in parameters.txt
        # z_for_map[:, :] =  parameters_valid_cases[:, 2][output_variables_for_map]
        z_for_map[:, :] =  parameters_valid_cases[:, 2][i]
    
    
    
        # x_for_predictions is a list. Every element of the list is a numpy array that 
        # contains all the elements that will be used for predictions. For instance, 
        # if the parameters.txt file has m columns, x_for_predictions will have 
        # m elements. Each element is a numpy array of all the values that variable 
        # will take at predicion time. 
        x_for_predictions = np.concatenate((x_for_map, y_for_map, z_for_map), axis = 2)
        x_for_predictions_scaled = x_scaler.transform(x_for_predictions.reshape([x_for_predictions.shape[0],
                                                                                 x_for_predictions.shape[2]] ))
        y_predictions_scaled = model.predict(x_for_predictions_scaled[:, np.newaxis, :])
        y_predictions = y_scaler.inverse_transform(y_predictions_scaled.reshape([y_predictions_scaled.shape[0], 
                                                                                 y_predictions_scaled.shape[2]]))
       
        
        plt.figure(figsize=(8, 6))
        plt.pcolormesh(x_for_predictions[:, :, 0].reshape([n_divisions_for_prediction, 
                                                           n_divisions_for_prediction]), 
                       x_for_predictions[:, :, 1].reshape([n_divisions_for_prediction, 
                                                           n_divisions_for_prediction]), 
                       y_predictions[:, i].reshape([n_divisions_for_prediction, 
                                                           n_divisions_for_prediction]), shading='auto')
        plt.colorbar(label="Predicted " + POSSIBLE_OUTPUTS[i] + " (m)")
        plt.xlabel(x_name)
        plt.ylabel(y_name)
        plt.title("Predictions using the NN")
        plt.tight_layout()
        # plt.show()
        plt.savefig(POSSIBLE_OUTPUTS[i]+ "_predictions.png")
    
    
def generate_processing_map(input_variables_for_map, parameters_valid_cases):
    # NOTE THIS FUNCTION IS NOT FINISHED, IT IS KEPT HERE TO GENERATE THE
    # CORRECT PLOT ONCE THE RULE TO DECIDE THE RULE TO DEFINE THE BOUNDARIES OF
    # THE REGIMES. FOR NOW, THIS FUNCTION JUST SHOWS THE CODE THAT 
    # GENERATES A SIMILAR COLOUR MAP, USING x_vals, x_vals and a synthetic
    # r value, calculated as a radius.
    x_vals, y_vals = generate_x_y_levels_for_predictions(parameters_valid_cases, 
                                                  x_ind=input_variables_for_map[0],
                                                  y_ind=input_variables_for_map[1])

    x, y = np.meshgrid(x_vals, x_vals)


    # 1. Create a simulated value
    r = np.sqrt(x**2 + y**2)  # aumenta con x e y

    distances = (x**2 + y**2)**0.5
    z = np.zeros(distances.shape)
    z[distances < 1.2] = 0
    z[(distances >= 1.2) & (distances <= 2)] = 1
    z[distances > 2] = 2


    z = z.astype(int)

    cmap = ListedColormap(['red', 'green', 'blue'])
    plt.figure(figsize=(8, 6))
    plt.pcolormesh(x, y, z, cmap=cmap, shading='auto')
    plt.xlabel('Scanning speed (mm/s)')
    plt.ylabel('Laser Power (W)')
    plt.title('Processing map')
    cbar = plt.colorbar(ticks=[0.5, 1.5, 2.5])
    cbar.ax.set_yticklabels(['Lack of fusion', 'Optimol', 'Overfusion'])
    plt.tight_layout()
    # plt.show()
    plt.savefig("Processing_map.png")
    

def is_meltpool_continuous(csv_file = "y_z_slice_meltpool.csv", 
                           print_missing_columns = False):
    df = pd.read_csv(csv_file)   
    continuous = True
    y = df["Points_1"].to_numpy()
    y0 = y.min()
    iy = np.rint((y - y0) / CELL_SIZE).astype(int)   # Y-column index
    present = np.unique(iy)
    first_c, last_c = present.min(), present.max()
    expected = np.arange(first_c, last_c + 1)
    
    missing = np.setdiff1d(expected, present)  # missing columns
    continuous = (missing.size == 0)
    
    if (print_missing_columns):
        print("Continuous (no missing Y columns):", continuous)
        if missing.size:
            # Ranges of the missing columns (useful for debugging)
            gaps = [(y0 + m*CELL_SIZE, y0 + (m+1)*CELL_SIZE) for m in missing]
            print("Missing Y columns (m):", gaps)
    
    dump(continuous, "./continuous.joblib")
    
    return continuous


def calculate_geometry_middle_sections(CSV_XZ = "x_z_slice_meltpool.csv", 
                                       MIN_POINTS_PER_ROW = 3, 
                                       print_results = False):
    df = pd.read_csv(CSV_XZ)
    x = df["Points_0"].to_numpy()
    z = df["Points_2"].to_numpy()

    # --- snap/quantize Z levels using known grid spacing ---
    DZ = CELL_SIZE  # assume Z spacing equals CELL_SIZE (grid is isotropic)

    # z = df["Points_2"].to_numpy()

    # Optionally align the origin to the grid (helps if z.min() is slightly off)
    z0 = z.min()
    z0_aligned = np.round(z0 / DZ) * DZ  # snap the origin to the nearest grid level

    # Number of rows from z0_aligned to z.max()
    nrows = int(np.round((z.max() - z0_aligned) / DZ)) + 1
    levels = z0_aligned + np.arange(nrows) * DZ  # exact Z levels of the grid

    # This is the CURING/QUANTIZATION step:
    # Map each raw z to an integer row index (nearest grid level)
    zi = np.rint((z - z0_aligned) / DZ).astype(int)
    zi = np.clip(zi, 0, nrows - 1)  # safety in case of tiny rounding overshoots

    # Optional: the "snapped" Z values (purely for inspection/export)
    z_snapped = levels[zi]
    # --------------------------------------------------------

    # --- sanity checks: look at the *snapped* uniqueness, not raw z ---
    if (print_results):
        print("raw unique z:", np.unique(z).size)
        print("unique row indices (zi):", np.unique(zi).size)
        print("unique snapped z:", np.unique(z_snapped).size)


    # --- width-by-row using the snapped indices ---
    rows = []
    for k in np.unique(zi):              # <--- unique on zi (snapped rows)
        mask = (zi == k)
        if mask.sum() < MIN_POINTS_PER_ROW:
            continue
        xk = x[mask]
        wk = xk.max() - xk.min()
        zk = levels[k]                   # exact snapped Z level for this row
        rows.append((k, zk, wk))

    if not rows:
        raise RuntimeError("No valid Z-rows found. Check MIN_POINTS_PER_ROW or input data.")

    # unpack rows -> arrays
    idx, z_levels, widths = zip(*rows)
    z_levels = np.array(z_levels, dtype=float)
    widths   = np.array(widths, dtype=float)

    # width: max horizontal chord across Z 
    max_width = float(widths.max())
    z_at_max  = float(z_levels[widths.argmax()])

    # height: total vertical extent of the (snapped) slice
    height = float(z_levels.max() - z_levels.min())

    # D
    D = float(z_at_max - z_levels.min())

    if (print_results):
        # report
        print(f"W:      {max_width:.3e} m")
        print(f"H (total Z span):  {height:.3e} m")
        print(f"D:        {D:.3e} m")
        print(f"Z at W_max:             {z_at_max:.3e} m")
        print(" ")

    dump(max_width, "./W.joblib")
    dump(height, "./H.joblib")
    dump(D, "./D.joblib")
    dump(z_at_max, "./z_at_max.joblib")



def calculate_geometry_full_meltpool(CSV_3D = "meltpool.csv", 
                                     MIN_POINTS_PER_ZROW = 3, 
                                     print_summary = False):
   
    df = pd.read_csv(CSV_3D)
    x = df["Points_0"].to_numpy()
    y = df["Points_1"].to_numpy()
    z = df["Points_2"].to_numpy()
    
    DX = DY = DZ = CELL_SIZE
    
    # snap Y and Z to grid indices (like part 2 for Z)
    y0 = float(np.floor(y.min() / DY) * DY)
    # z0 = float(np.floor(z.min() / DZ) * DZ)
    z0_aligned = float(np.round(z.min() / DZ) * DZ)   # same as Part 2
    iy = np.rint((y - y0) / DY).astype(int)
    # iz = np.rint((z - z0) / DZ).astype(int)
    iz = np.rint((z - z0_aligned) / DZ).astype(int)
        
    def xz_metrics_for_section(x_sec, iz_sec, DZ, z0_aligned, min_pts_per_row=3):
        """
        Replicates Pprevious function on an XZ slice at fixed Y, using snapped Z semantics:
          - W: max horizontal chord in X across snapped Z rows
          - height:    (kz_max - kz_min) * DZ               [snapped]
          - Z_at_D:    z0_aligned + kz_at_max_width * DZ          [snapped]
          - D:         (kz_at_max_width - kz_min) * DZ            [snapped]
        """
        if x_sec.size == 0 or iz_sec.size == 0:
            return np.nan, np.nan, np.nan, np.nan
    
        # Build w(z) over snapped rows
        widths = []
        for kz in np.unique(iz_sec):
            m = (iz_sec == kz)
            if m.sum() < min_pts_per_row:
                continue
            xk = x_sec[m]
            wk = float(xk.max() - xk.min())
            widths.append((kz, wk))
    
        if not widths:
            # No valid rows: we can still report height from iz indices (0 if empty)
            if iz_sec.size == 0:
                return np.nan, np.nan, np.nan, np.nan
            kz_min = int(np.min(iz_sec))
            kz_max = int(np.max(iz_sec))
            height = float((kz_max - kz_min) * DZ)
            return np.nan, height, np.nan, np.nan
    
        kz_list, w_vals = map(np.array, zip(*widths))
        kmax = int(np.argmax(w_vals))
        W = float(w_vals[kmax])
    
        # Snapped indices for bottom/top
        kz_at_max_width = int(kz_list[kmax])
        kz_min   = int(np.min(iz_sec))
        kz_max   = int(np.max(iz_sec))
    
        # Snapped outputs (match Part 2)
        Z_at_D = float(z0_aligned + kz_at_max_width * DZ)
        height = float((kz_max - kz_min) * DZ)
        D      = float((kz_at_max_width - kz_min) * DZ)
    
        return W, height, Z_at_D, D
    
    
    # iterate all Y sections
    records = []
    for ky in np.unique(iy):
        mY = (iy == ky)
        width, height, Z_at_D, D = xz_metrics_for_section(
            x_sec=x[mY], iz_sec=iz[mY],
            DZ=DZ, z0_aligned=z0_aligned,
            min_pts_per_row=MIN_POINTS_PER_ZROW
        )
        y_pos = float(y0 + ky * DY)  # snapped Y position
        records.append({
            "y_m": y_pos,
            "width_m": width,
            "height_m": height,
            "Z_at_D_m": Z_at_D,
            "D_m": D,
            "n_points": int(mY.sum())
        })
    
    out = pd.DataFrame.from_records(records).sort_values("y_m").reset_index(drop=True)
    out.to_csv("section_metrics_along_y.csv", index=False)
    dump(out, "section_metrics_along_y.joblib")
    
    # global mean/std across sections (skip NaNs)
    summary = {
        "width_mean_m": float(out["width_m"].mean(skipna=True)),
        "width_std_m":  float(out["width_m"].std(skipna=True, ddof=1)),
        "height_mean_m":    float(out["height_m"].mean(skipna=True)),
        "height_std_m":     float(out["height_m"].std(skipna=True, ddof=1)),
        "D_mean_m": float(out["D_m"].mean(skipna=True)),
        "D_std_m":  float(out["D_m"].std(skipna=True, ddof=1)),
        "n_sections": int(len(out))
    }
    pd.Series(summary).to_csv("section_metrics_summary_y.csv")
    dump(summary, "section_metrics_summary_y.joblib")
    
    if (print_summary):
        print("Computed Y-sections:", len(out))
        print(out.head(6))
        print("\nSummary:", summary)



def calculate_statistics_rows_meltpool(CSV_3D = "meltpool.csv"):
    
    # This function takes the .csv file tht represents the meltpool and 
    # calculates several metrics for every row in the meltpool. 
    # The resulting objects are: 
    # 1. Statistics = [id_row, y_coord, z_coord_ x_min, x_max, 
    # row_has_pores, number_of_pores_in_row, width_row, 
    # number_non_void_cells_in_row]
    # 2. pore_locatios_at_rows = A file with "NA" if the row has no pores. 
    # Otherwise, it has list with the x_coord of every pore at the row
    # 3. pores_at_row_are_internal = A file with "NA" if the row has no pores.
    # Otherwise, it has "True" or "False" for every pore in the row. True if 
    # the pore is internal, Flase, otherwise
    
    df = pd.read_csv(CSV_3D)
    x = df["Points_0"].to_numpy()
    y = df["Points_1"].to_numpy()
    z = df["Points_2"].to_numpy()
       
    y0 = 140e-6 #This is the number I have to link to the laser radius
    y_max = 660e-6 # This number must also be lined to the laser aradius
    factor = 1000
    TOL = CELL_SIZE/factor

    iy = y0
    id_row = 0
    
    # Statistics [id_row, y_coord, z_coord_ x_min, x_max, row_has_pores, 
    # number_of_pores_in_row, width_row, number_non_void_cells_in_row]
    Statistics = []
    pore_locatios_at_rows = []
    pores_at_row_are_internal = []
    
    
    # Iterate over all the y-sections
    while (iy <= y_max):

        mask = (iy == np.round(y, 8))
        cells_at_iy = df[mask]
        x_at_iy = cells_at_iy["Points_0"].to_numpy()
        y_at_iy = cells_at_iy["Points_1"].to_numpy()
        z_at_iy = cells_at_iy["Points_2"].to_numpy()

        if (z_at_iy.shape[0] == 0):
            print("HEREEE")
        
        z_min_at_iy = np.min(z_at_iy)
        z_max_at_iy = np.max(z_at_iy)
        x_min_at_iy = np.min(x_at_iy) 
        x_max_at_iy = np.max(x_at_iy) 
        
        z_min_at_iy_that_is_in_original_mesh = np.round(np.round(z_min_at_iy/CELL_SIZE) * CELL_SIZE, 8)
        z_max_at_iy_that_is_in_original_mesh = np.round(np.round(z_max_at_iy/CELL_SIZE) * CELL_SIZE, 8)
        x_min_at_iy_that_is_in_original_mesh = np.round(np.round(x_min_at_iy/CELL_SIZE) * CELL_SIZE, 8)
        x_max_at_iy_that_is_in_original_mesh = np.round(np.round(x_max_at_iy/CELL_SIZE) * CELL_SIZE, 8)
        
        
        iz = z_min_at_iy_that_is_in_original_mesh
        
        while (iz <= z_max_at_iy_that_is_in_original_mesh):
            mask2 = ((iz == np.round(z_at_iy, 8)))
            cells_at_iy_iz = cells_at_iy[mask2]
            x_at_iy_iz = cells_at_iy_iz["Points_0"].to_numpy()
            if (x_at_iy_iz.shape[0] == 0):
                iz = z_max_at_iy_that_is_in_original_mesh
                          
            else:
                min_x_at_iy_iz = np.min(x_at_iy_iz)
                max_x_at_iy_iz = np.max(x_at_iy_iz)
                
                
                min_x_at_iy_iz_that_is_in_original_mesh = np.round(np.round(min_x_at_iy_iz/CELL_SIZE) * CELL_SIZE, 8)
                max_x_at_iy_iz_that_is_in_original_mesh = np.round(np.round(max_x_at_iy_iz/CELL_SIZE) * CELL_SIZE, 8)
                
                distance_minx_max_at_zlevel = np.round(
                    max_x_at_iy_iz_that_is_in_original_mesh - 
                    min_x_at_iy_iz_that_is_in_original_mesh, 8)
                expected_number_cells_at_iy_iz = int(distance_minx_max_at_zlevel/CELL_SIZE)
               
                ix = min_x_at_iy_iz_that_is_in_original_mesh
                init_in = ix
                number_non_void_cells_in_row = 0
                
                row_has_pores = False
                n_pores_in_row = 0
                width_row = np.round(max_x_at_iy_iz_that_is_in_original_mesh - 
                                     min_x_at_iy_iz_that_is_in_original_mesh, 
                                     8)
                
                pore_locations_at_row_i = []
                pores_at_row_i_are_internal = []
                if (expected_number_cells_at_iy_iz > 1):
                    while (ix < max_x_at_iy_iz_that_is_in_original_mesh):
                        if (np.sum([ix == np.round(x_at_iy_iz, 8)]) > 0):
                            cell_is_a_pore = False
                            number_non_void_cells_in_row = (
                                              number_non_void_cells_in_row + 1)
                        else:
                            cell_is_a_pore = True
                            n_pores_in_row = n_pores_in_row + 1
                            row_has_pores = True
                            pore_locations_at_row_i.append(ix)
                            mask3 = (ix == np.round(x_at_iy, 8))
                            cells_at_ix_iy = cells_at_iy[mask3]
                            z_at_ix_iy = cells_at_ix_iy["Points_2"]
                            pores_at_row_i_are_internal.append(
                                                   np.sum(iz < z_at_ix_iy) > 0)
                                                    
                        ix = np.round(ix + CELL_SIZE, 8)
                
                if (n_pores_in_row > 0):
                    pore_locations_at_row_i.insert(0, id_row)
                    pore_locatios_at_rows.append(pore_locations_at_row_i)
                    pores_at_row_i_are_internal.insert(0, id_row)
                    pores_at_row_are_internal.append(pores_at_row_i_are_internal)
                else:
                    pore_locatios_at_rows.append([id_row, "NA"])
                    pores_at_row_are_internal.append([id_row, "NA"])
                
                        
                new_statistics_row = [id_row, iy, iz, 
                                      min_x_at_iy_iz_that_is_in_original_mesh, 
                                      max_x_at_iy_iz_that_is_in_original_mesh, 
                                      row_has_pores, n_pores_in_row, width_row,
                                      number_non_void_cells_in_row]
                
                Statistics.append(new_statistics_row)
                print(Statistics[-1])
                print(" ")

                iz = np.round(iz + CELL_SIZE, 8)
                id_row = id_row + 1
        
        iy = np.round(iy + CELL_SIZE, 8)


    row_statistics = pd.DataFrame(Statistics, columns = ["id_row", "y_coord", 
                                                          "z_coord_", "x_min", 
                                                          "x_max", 
                                                          "row_has_pores", 
                                                      "number_of_pores_in_row", 
                                                          "width_row",
                                               "number_non_void_cells_in_row"])
    row_statistics.to_csv("row_statistics.csv", index=False, encoding="utf-8") 
    
    return row_statistics, pore_locatios_at_rows, pores_at_row_are_internal


def calculate_cross_sections_statistics(row_statistics, pore_locatios_at_rows, 
                                        pores_at_row_are_internal):
    cross_sections_statistics = []
    y = row_statistics["y_coord"].to_numpy()
    row_has_pores = row_statistics["row_has_pores"]
    y_unique = np.unique(y)  
    
    for iy in y_unique:
        mask = (iy == y)
        cross_section_at_iy = row_statistics[mask]
        z_at_iy = cross_section_at_iy["z_coord_"]
        pores_at_iy = cross_section_at_iy["row_has_pores"]
        id_rows_at_iy = cross_section_at_iy["id_row"]
        width_rows_at_iy = cross_section_at_iy["width_row"]
        number_pores_at_iy = cross_section_at_iy["number_of_pores_in_row"]
        number_non_void_cells_in_row_at_iy = cross_section_at_iy["number_non_void_cells_in_row"]
        max_height_location_at_iy = 0 # Just initialisation
        i = min(id_rows_at_iy)
        
        if (True not in pores_at_iy.values): # This means there is no holes at this iy section, neither internal nor upper boundaries
            max_height_location_at_iy = z_at_iy[max(id_rows_at_iy)]
            height =  max_height_location_at_iy - min(z_at_iy)
            width = max(width_rows_at_iy)
            z_location_max_width = width_rows_at_iy.argmax(width)
            depth = max(z_at_iy) - z_at_iy.to_numpy()[z_location_max_width]
        
        else:
            while (i < max(id_rows_at_iy)):
                if (pores_at_iy[i]):
                    if (True not in pores_at_row_are_internal[i]): # This means all the pores are upper boundaries
                        max_height_location_at_iy = z_at_iy[i]
                        height =  max_height_location_at_iy - min(z_at_iy)
                        i = max(id_rows_at_iy) # # Break the loop
                    elif (False not in pores_at_row_are_internal[i]): #This means all the pores are internal
                        pass
                    else:
                        pass
                i = i + 1
            
            if (max_height_location_at_iy == 0): # This means the iy section has holes, but they are internal 
                max_height_location_at_iy = z_at_iy[i-1]
                height =  max_height_location_at_iy - min(z_at_iy)
                
            mask2 = (z_at_iy < max_height_location_at_iy)
            possible_max_widths = width_rows_at_iy[mask2]
            width = max(possible_max_widths)
            location_top_depth_level = np.argmax(possible_max_widths)       
            depth = ((z_at_iy).to_numpy())[location_top_depth_level] -  min(z_at_iy)
        
        # print(iy, width, height, depth)
        porous_volume_at_iy = np.sum(number_pores_at_iy.to_numpy())
        total_volume_material_at_iy = (np.sum(number_non_void_cells_in_row_at_iy.to_numpy()) + 
                                             np.sum(number_pores_at_iy.to_numpy()))
        
        porosity_at_iy = porous_volume_at_iy/total_volume_material_at_iy
        cross_sections_statistics.append([iy, width, height, depth, 
                                          porosity_at_iy])
          
    return pd.DataFrame(cross_sections_statistics, columns = ["iy", "width", 
                                                              "height", 
                                                              "depth", 
                                                             "porosity_at_iy"])


def calculate_geometry_full_meltpool2(CSV_3D = "meltpool.csv", 
                                     MIN_POINTS_PER_ZROW = 3, 
                                     print_summary = False):

    row_statistics, pore_locatios_at_rows, pores_at_row_are_internal = calculate_statistics_rows_meltpool(CSV_3D)

    cross_sections_statistics = calculate_cross_sections_statistics(row_statistics, pore_locatios_at_rows, pores_at_row_are_internal)
    



def plot_history_training(history, destination_file):
    # Plot loss vs. epochs
    plt.plot(history.history['loss'], label='Training loss')
    plt.plot(history.history['val_loss'], label='Validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    # plt.show()
    plt.savefig(destination_file + "/loss_vs_iterations.png", dpi=300)  # saves as PNG (high res)
    