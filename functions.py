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
  Auxiliary functions required by the simulation driver program.

Authors
    Simon A. Rodriguez, University College Dublin (UCD). All rights reserved
    Petar Cosic, University College Dublin (UCD). All rights reserved
    Tom Flint, University of Manchester. All rights reserved
    Philip Cardiff, University College Dublin (UCD). All rights reserved
'''


import os
import input_data
from input_data import *

def terminal(command):
    os.system(command)

def create_test_case(base_case_name, test_case_number):
    name_new_folder = MESH_DENSITY + "/test_case_" + str(test_case_number + 1)
    terminal("mkdir -p "  + name_new_folder)
    # terminal("cp -r base_case/* " + name_new_folder)
    terminal("cp -r " + base_case_name + "/* " + name_new_folder)
    terminal("cp -r *py " + "./" + name_new_folder)
    
    
    
def replace_speed_power_radius(variable, value):

        
    if (variable == "radius"):
        # Replace the laser radius in the correct file, depending on simulation case
        file_name = "./" + name_new_folder + "/constant/laserProperties"
        # Read all lines in the file
        with open(file_name, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if (OPENFOAM_VERSION == "2412"):
            lines[17] = "laserRadius " + str(value) + "; // The radius of the laser \n"  
        else:
            lines[16] = "\tr0\t\t  " + str(value) +"; //25e-6;\n"
            
        # Write the new lines in the file 
        with open(file_name, 'w', encoding='utf-8') as f:
            f.writelines(lines)
