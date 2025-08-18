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
OPENFOAM_VERSION = "2412" # Or "FE40"


# FINE for ~2 million cells.
# COARSE for ~1Million cells. 
MESH_DENSITY = "COARSE"  #"FINE" # "COARSE"  
CELL_SIZE = 4e-06
# LASER_SPOT_SIZE = 80e-6 # 80 microns

n_epochs = 100
n_divisions_for_prediction = 50# 50#10


POSSIBLE_OUTPUTS = ["W", "H", "D"]
# # n_outputs = 3 # width, depth, depth-to-flat

SEED = 0
STATUS_CHECK_FREQUENCY_IN_MIN = 1 # 15