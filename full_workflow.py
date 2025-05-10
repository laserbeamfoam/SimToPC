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

import functions
from functions import *
import numpy as np
import input_data
from input_data import *



import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


OF9_EV_LOCATION = "/opt/openfoam9/etc/bashrc"
FE_40_LOCATION = "/home/simon/foam/foam-extend-4.0/etc/bashrc"
terminal("pwd")

print("Running blockMesh")
terminal(f'bash -c "source {FE_40_LOCATION} && cd base_case && blockMesh"')

print("Running setSolidFraction")
terminal(f'bash -c "source {FE_40_LOCATION} && cd base_case && setSolidFraction"')



# Read the data
parameters = np.loadtxt("./parameters.txt", skiprows=1)

number_cases = parameters.shape[0]
number_of_variables = parameters.shape[1]

# Create the test cases
for i in range(number_cases):
    name_new_folder = "test_case_" + str(i+1)
    terminal("mkdir -p " + name_new_folder)
    terminal("cp -r base_case/* " + name_new_folder)
    terminal("cp -r *py " + name_new_folder)
    
    
    file_name = "./" + name_new_folder + "/constant/laserProperties"
    # Read all lines in the file
    with open(file_name, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    lines[16] = "\tr0\t\t  " + str(parameters[i, 0]) +"; //25e-6;\n"

    # Write the new lines in the file 
    with open(file_name, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
    
    
# Transfer the test cases to the HPC system
for i in range(number_cases):
    name_new_folder = "test_case_" + str(i+1)
    print("Transferring the test case ", str(i+1))

    terminal("scp -r " + name_new_folder +  
              " meluxina:/project/home/p200734/Simon/GowthamanSolver/run/" + 
              "runs_coarse_mesh")



run_next = "yes"
i = 0
if (run_next == "yes" and i < number_cases):
    # Run the simulations
    for i in range(number_cases):   
        name_new_folder = "test_case_" + str(i+1)
        terminal(f'ssh meluxina "cd /project/home/p200734/Simon/GowthamanSolver/run/runs_coarse_mesh/{name_new_folder} && sbatch singleTrack.sh"')
        # Ask the user whether to run new simulations
        if (i < number_cases - 1):
            run_next = input("Do you want to run new simulations? (yes/no): ").strip().lower()


# Pull the results
pull_results_flag = input("Should I pull the results now? (yes/no): ").strip().lower()
if (pull_results_flag == "yes"):
    for i in range(number_cases):
        name_new_folder = "test_case_" + str(i+1)
        print("Pulling results from " + name_new_folder)
        terminal("cd " + name_new_folder + " && rm -r processor*")
        terminal("cd " + name_new_folder + "  && scp -r meluxina:/project/home/p200734/Simon/GowthamanSolver/run/runs_coarse_mesh/" + name_new_folder + "/* .")


# Calculate results (width, depth, etc)
for i in range(number_cases):
    name_new_folder = "test_case_" + str(i+1)
    # terminal("bash ~/foam/foam-extend-4.0/etc/bashrc && ls && python postproc2.py && quantitiesFromMeltpool.py ")
    # terminal("bash ~/ && ls && python postproc2.py && quantitiesFromMeltpool.py ")
    # terminal("source " + OF9_EV_LOCATION + " &&  icoFoam --help && cd " + name_new_folder + " && pwd && pvpython postproc2.py")
    # terminal('bash -c "source /opt/openfoam9/etc/bashrc && which icoFoam"')
    # terminal('bash -c "source /opt/openfoam9/etc/bashrc && pwd && cd {name_new_folder}"')
    terminal(f'bash -c "source {OF9_EV_LOCATION} && which icoFoam && cd {name_new_folder} && pvpython postproc2.py"')


# Check all the cases ran properly
for i in range(number_cases):
    name_new_folder = "test_case_" + str(i+1)
    files_in_folder_i = os.listdir("./" + name_new_folder)

    # Verificar si "finished.txt" está en la lista
    if 'finished.txt' in files_in_folder_i:
        pass
    else:
        print(name_new_folder + "did not run properly")
        print("Check the simulations that failed")
        break



# Assemble the training set
width_data = np.zeros((number_cases, 1))
depth_data = np.zeros((number_cases, 1))
height_to_flat_data = np.zeros((number_cases, 1))
for i in range(number_cases):
    name_new_folder = "test_case_" + str(i+1)
    width_data[i, 0] = np.load("./" + name_new_folder + "/width.npy")
    depth_data[i, 0] = np.load("./" + name_new_folder + "/depth.npy")
    height_to_flat_data[i, 0] = np.load("./" + name_new_folder + "/height_to_flat.npy")

    
    

# Set the neural network up
model = Sequential()
model.add(Dense(units = 10, 
                kernel_initializer = 'he_normal', 
                activation = 'relu', input_shape = (None, 2)))
model.add(Dense(units = 3, kernel_initializer = 'he_normal', 
                activation = 'linear'))

# # Train the neural network
width_data = width_data.reshape((number_cases, 1, 1))
depth_data = depth_data.reshape((number_cases, 1, 1))
height_to_flat_data = height_to_flat_data.reshape((number_cases, 1, 1))

input_data = parameters.reshape((number_cases, 1, parameters.shape[1]))
output_data = np.concatenate((width_data, depth_data, height_to_flat_data), axis = 2)


model.compile(optimizer=Adam(lr = 0.01), loss='mse')

# Train the ML model
history = model.fit(input_data, 
                        output_data, 
                        epochs = 10, 
                        validation_split = 0.01)


######## I probably do not need the code in this section ############
# Make predicions
points_distance_to_origin = (parameters[:, 0]**2 + parameters[:, 1]**2)**0.5 
minimum_distance = min(points_distance_to_origin) # This line is just for reference
minimum_distance_index = np.argmin(points_distance_to_origin)

maximum_distance = max(points_distance_to_origin) # This line is just for reference
maximum_distance_index = np.argmax(points_distance_to_origin)
###########################################################################


# Generate the plot
x_vals = np.linspace(min(parameters[:, 1]), max(parameters[:, 1]), 50)
y_vals = np.linspace(min(parameters[:, 0]), max(parameters[:, 1]), 50)

x, y = np.meshgrid(x_vals, y_vals)


# Reshape x and y to make predictions with the NN
x_training = x.reshape((x.shape[0] * x.shape[0], 1))
y_training = y.reshape((y.shape[0] * y.shape[0], 1))

# Make predictions
x_training = np.concatenate((x_training, y_training), axis = 1)
x_training = x_training.reshape((x_training.shape[0], 1, 2))
y_predicted = model.predict(x_training)

width_predicted = y_predicted[:, :, 0].reshape((int(y_predicted.shape[0]**0.5), int(y_predicted.shape[0]**0.5)))
depth_predicted = y_predicted[:, :, 1].reshape((int(y_predicted.shape[0]**0.5), int(y_predicted.shape[0]**0.5)))
height_to_flat_predicted = y_predicted[:, :, 2].reshape((int(y_predicted.shape[0]**0.5), int(y_predicted.shape[0]**0.5)))


# These z-values should be replaced with the ones from the model once it has been trained with simulation results, i am doing it with this for now for testing purposes
distances = (x**2 + y**2)**0.5
z = np.zeros(distances.shape)
z[distances < 1.8] = 0
z[(distances >= 1.8) & (distances <= 2.5)] = 1
z[distances > 2.5] = 2



cmap = ListedColormap(['red', 'green', 'blue'])


plt.figure(figsize=(8, 6))
plt.pcolormesh(x, y, z, cmap=cmap, shading='auto')
plt.xlabel('Scanning speed (mm/s)')
plt.ylabel('Laser Power (W)')
plt.title('Processing map')
cbar = plt.colorbar(ticks=[0.5, 1.5, 2.5])
cbar.ax.set_yticklabels(['Lack of fusion', 'Optimol', 'Overfusion'])
plt.tight_layout()
plt.show()




















