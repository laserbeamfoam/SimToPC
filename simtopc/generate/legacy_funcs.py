"""
License
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published
  by the Free Software Foundation, either version 3 of the License,
  or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

  See the GNU General Public License for more details.
  You should have received a copy of the GNU General Public License
  along with this program. If not, see <https://www.gnu.org/licenses/>.

Description
  Legacy utility functions supporting the simulation-case generation
  workflow in SimToPC.

  This module provides low-level helper routines used to:
  - create simulation cases from a base OpenFOAM case,
  - modify OpenFOAM dictionary files with process parameters,
  - submit and monitor simulation jobs locally or on HPC systems,
  - handle file transfer, compression, and basic workflow orchestration.

  The functions defined here are primarily intended for internal use
  by higher-level SimToPC workflows and scripts.

Assumptions
  - This module is invoked by higher-level SimToPC generation routines
  - OpenFOAM case dictionaries follow the expected solver-specific structure
  - Remote job submission relies on passwordless SSH access when enabled
  - The execution environment provides standard UNIX utilities

Authors
  Simon A. Rodriguez, University College Dublin (UCD)
  Alojz Ivankovic, University College Dublin (UCD)
  Petar Cosic, University College Dublin (UCD)
  Tom Flint, University of Manchester (UoM)
  Philip Cardiff, University College Dublin (UCD)
"""



import os
import re
from joblib import dump, load
import numpy as np
import pandas as pd
import random
import subprocess
import time
import importlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import shutil
from pathlib import Path


def terminal(command):
    os.system(command)

def set_environment_variables(RUNNING_ON):   
    variables_import = "input_files."+ RUNNING_ON.lower() + "_inp" 
    imported = importlib.import_module(
        f"simtopc.generate.input_files.{RUNNING_ON.lower()}_inp"
    )
    hostname = imported.hostname
    run_address = imported.run_address
    OF_LOCATION = imported.OF_LOCATION
    return hostname, run_address, OF_LOCATION

def set_base_case_name(MESH_DENSITY, OPENFOAM_VERSION):
    BASE_CASE_NAME = ""
    if (OPENFOAM_VERSION == "2412"):
        BASE_CASE_NAME = MESH_DENSITY + "/base_case_of2412"
    else:
        BASE_CASE_NAME = MESH_DENSITY + "base_case_fe40"
        
    return BASE_CASE_NAME
    

def create_test_case(base_case_name, test_case_number, MESH_DENSITY):
    """
    Create a test case directory and copy the contents of the base case into 
    it. This version is portable (doesn't depend on the current working 
    directory).
    """
    name_new_folder = str(
        Path(MESH_DENSITY) / f"test_case_{test_case_number + 1}"
    )

    case_dir = Path(name_new_folder).resolve()
    base_case = Path(base_case_name).resolve()

    if not base_case.exists():
        raise FileNotFoundError(f"Base case folder not found: {base_case}")

    case_dir.mkdir(parents=True, exist_ok=True)

    # Copy contents of base_case into case_dir
    for item in base_case.iterdir():
        dest = case_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)


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
        # in_scope = (current_blocks == block_path) if block_path else 
        # (len(current_blocks) == 0)
        in_scope = (
                    (current_blocks == block_path)
                    if block_path
                    else (len(current_blocks) == 0)
                    )

        # Case 1: Double key + dimensions (e.g. "cpL cpL [dims] valor;")
        pattern_dims =rf'^(\s*{key}\s+{key}\s+\[[^\]]+\]\s+)([^\s;]+)(\s*;.*)$'
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

        # Caso 3: Keys with no dimensions (e.g. "ray_tracing_on false;")
        pattern_nodims = rf'^(\s*{key}\s+)([^\s;]+)(\s*;.*)$'
        match_nodims = re.match(pattern_nodims, line)
        if in_scope and match_nodims:
            prefix, _, suffix = match_nodims.groups()
            new_line = f"{prefix}{new_value}{suffix}\n"
            new_lines.append(new_line)
            continue
        
        # Case 4: Qualifier + value: "h uniform 0;" or "Ta constant 298;"
        pattern_qual =rf'^(\s*{key}\s+)(uniform|constant)\s+([^\s;]+)(\s*;.*)$'
        m_qual = re.match(pattern_qual, line)
        if m_qual:
            prefix, qualifier, _, suffix = m_qual.groups()
            new_lines.append(f"{prefix}{qualifier} {new_value}{suffix}\n")
            continue

        # If it does no coincide with anything, maintain the original line
        new_lines.append(line)

    with open(file_path, 'w') as f:
        f.writelines(new_lines)

    print(f"✅ '{full_key}' updated to {new_value}")


def replace_speed(value, test_case_number, MESH_DENSITY, OPENFOAM_VERSION):
    name_new_folder = MESH_DENSITY + "/test_case_" + str(test_case_number + 1)
    file_name = str(Path(name_new_folder) / "constant" / "timeVsLaserPosition")

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
            

def replace_power(value, test_case_number, speed, MESH_DENSITY, 
                  OPENFOAM_VERSION):
    name_new_folder = MESH_DENSITY + "/test_case_" + str(test_case_number + 1)
    file_name = str(Path(name_new_folder) / "constant" / "timeVsLaserPower")

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
  

def create_simulation_cases(number_cases, base_case_name, parameters, 
                            MESH_DENSITY, OPENFOAM_VERSION):
    # Create the simulation cases
    for i in range(number_cases):    
        name_new_folder = MESH_DENSITY + "/test_case_" + str(i + 1)
        os.makedirs(name_new_folder, exist_ok=True)

        # Create the test cases
        create_test_case(base_case_name, i, MESH_DENSITY)
        
        #Replace the correct values for radius,
        update_openfoam_variable(name_new_folder + 
                                  "/constant/laserProperties", "laserRadius", 
                                  parameters[i, 2]/2)

    
        #Replace the correct values for scanning speed
        replace_speed(parameters[i, 0], i, MESH_DENSITY, OPENFOAM_VERSION)
    
        #Replace the correct values for power
        replace_power(parameters[i, 1], i, parameters[i, 0], MESH_DENSITY, 
                      OPENFOAM_VERSION)


def submit_remote_job(remote_host, remote_case_path, local_case_path, 
                      RUNNING_ON):
    # Submit job on HPC via SSH
    cmd = (
        f'ssh {remote_host} "cd {remote_case_path} '
        f'&& sbatch singleTrack{RUNNING_ON}.sh"'
    )

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


def monitor_job_is_running(id_current_job, hostname, 
                           STATUS_CHECK_FREQUENCY_IN_MIN):
    is_current_job_in_queue = True
    while (is_current_job_in_queue):
        is_current_job_in_queue = is_job_in_queue(id_current_job, hostname)
        if (is_current_job_in_queue):
            print("Job ", str(id_current_job), " is still in the queue")
            time.sleep(STATUS_CHECK_FREQUENCY_IN_MIN * 60)  # Sleep for X mints
        else:
            print("Job ", str(id_current_job), " is finished")