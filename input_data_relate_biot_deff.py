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
  Central configuration file for the workflow:
  - Defines execution environment (local or HPC system)
  - Sets OpenFOAM version and mesh density
  - Acts as a single source of truth for other scripts

Assumptions:
  - Must be edited before running to reflect the target system setup
  - Expected to match the version of OpenFOAM and solver in use

Authors
    Simon A. Rodriguez, University College Dublin (UCD). All rights reserved
    Petar Cosic, University College Dublin (UCD). All rights reserved
    Tom Flint, University of Manchester (UOM). All rights reserved
    Philip Cardiff, University College Dublin (UCD). All rights reserved

'''



RUNNING_ON = "Xenosim" 
OPENFOAM_VERSION = "2412" 


# FINE for ~2 million cells.
# COARSE for ~1Million cells. 
MESH_DENSITY = "COARSE"  #"FINE" # "COARSE"  
CELL_SIZE = 2.5e-06
DOMAIN_SIZE_IN_MICRONS = [200, 800, 200] # x, y, z
Y_COORD_BEGIN_TRACK = 100e-6
Y_COORD_END_TRACK = 700e-6
X_MIN_AND_MAX_DOMAIN = [0, 0.0002]

relate_biot_and_effective_distance = True

T_solidus = 1658 # in K
K_at_T_solidus = 6.31 + (27.2e-3) * T_solidus - 7e-6 * T_solidus**2 #in W/(m * K)

# For training the NN
n_epochs = 500

# How many points will be plotted when predicting with the NN, both in x and y
n_divisions_for_prediction = 50# 50# 50#10


# POSSIBLE_OUTPUTS = ["W", "H", "D"]
POSSIBLE_OUTPUTS = ["W_mean", "W_std", "H_mean", "H_std", "D_mean", "D_std", "Porosity_mean", "Porosity_std"]

# For reproducibility
SEED = 0

# This number indicates how often it will be checked if whether a job is being
# run on the HPC system 
STATUS_CHECK_FREQUENCY_IN_MIN = 1 # 15
