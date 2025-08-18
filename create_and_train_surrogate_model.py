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

import os
import numpy as np
import random
import re
from functions import (create_width_depth_height_to_flat_data, create_NN, 
                       create_scalers, create_input_data_and_output_data, 
                       fit_scalers, scale_data, seed_everything, 
                       define_good_simulation_cases,
                       generate_x_y_levels_for_predictions, 
                       generate_prediction_map, generate_processing_map)

from input_data import (SEED, MESH_DENSITY, n_epochs, 
                       n_divisions_for_prediction, POSSIBLE_OUTPUTS)
from joblib import dump, load

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.preprocessing import MinMaxScaler
from itertools import combinations


# Seed everything 
seed_everything(SEED)

# Read the operational parameters
parameters = np.loadtxt("./parameters.txt", skiprows=1)

# Count the total number of cases
number_cases = parameters.shape[0]

# Count the total number of operational parameters to evaluate
number_of_variables = parameters.shape[1]

# Check all the cases ran properly
# good_simulation_cases is a List of the cases that ran properly
good_simulation_cases = define_good_simulation_cases(MESH_DENSITY, 
                                                     number_cases)
    
# width_data is a list W from every simulation
# depth_data is a list H from every simulation
# height_to_flat_data is a list D from every simulation
width_data, depth_data, height_to_flat_data, \
cases_ran_properly_and_have_continuous_meltpool = \
    create_width_depth_height_to_flat_data(good_simulation_cases)


# Create and compile a Keras-based fully-connected neural network
model = create_NN(10, 3, 3)

# Count the number of useful cases, this is, cases that ran OK and have
# continuous meltpools
number_useful_cases = cases_ran_properly_and_have_continuous_meltpool.shape[0]    


# Create the scalers
x_scaler, y_scaler = create_scalers()


# # Create the data for the NN
input_data, output_data, parameters_valid_cases = \
    create_input_data_and_output_data(width_data, depth_data, 
                                      height_to_flat_data, number_useful_cases, 
                               cases_ran_properly_and_have_continuous_meltpool,
                               parameters)

# Fit the scalers
fit_scalers(x_scaler, y_scaler, input_data, output_data)


# Scale the input and output
input_data_scaled, output_data_scaled = scale_data(x_scaler, y_scaler, 
                                                   input_data, output_data)


# Make input and output data 3D for the NN
input_data_scaled = input_data_scaled[:, np.newaxis, :]
output_data_scaled = output_data_scaled[:, np.newaxis, :]

# Train the ML model
history = model.fit(input_data_scaled, output_data_scaled, epochs = n_epochs, 
                    validation_split = 0.01)

# Save the trained neural network
model.save("NN.h5")



######### Processing map generation  ###############

# It is possible to generate a processing map, this is, a x-y figure where all 
# the x-y combinations are tested and a z variable is plotted and the colour 
# represents its magnitude. This is, it is possible to create a z-field
# over the x-y space. 

# Note that the default setup in this code assumes the parameters.txt has 
# 3 variables: speed, power, laser spot size and 3 geometric quantities are 
# estimated: W, H, D. 

# To generate the processing map, 2 input variables and 1 output variables 
# must be selected. 

input_variables_for_map = [0, 1]  # This must be defined by the user. They will
                                  # be x and y in the figure. In this case, 
                                  # 0 corresponds to speed and 1 corresponds
                                  # to power
                                  
output_variables_for_map = 0 # [0]  # The index of the variable of interest in 
                                # POSSIBLE_OUTPUTS  


generate_prediction_map(input_variables_for_map, output_variables_for_map, 
                        parameters_valid_cases, x_scaler, y_scaler, model, 
                        POSSIBLE_OUTPUTS, x_name ="Scanning speed (m/s)", 
                        y_name = "Power (W)")


# NOTE THIS FUNCTION IS NOT FINISHED, IT IS KEPT HERE TO GENERATE THE
# CORRECT PLOT ONCE THE RULE TO DECIDE THE RULE TO DEFINE THE BOUNDARIES OF
# THE REGIMES. FOR NOW, THIS FUNCTION JUST SHOWS THE CODE THAT 
# GENERATES A SIMILAR COLOUR MAP, USING x_vals, x_vals and a synthetic
# r value, calculated as a radius.
generate_processing_map(input_variables_for_map, parameters_valid_cases)

print("Thanks for using this software.")