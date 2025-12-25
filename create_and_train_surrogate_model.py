'''
License
    This programme is free software: you can redistribute it and/or modify 
    it under the terms of the GNU General Public License as published 
    by the Free Software Foundation, either version 3 of the License, 
    or (at your option) any later version.
    
    This programme is distributed in the hope that it will be useful, 
    but WITHOUT ANY WARRANTY; without even the implied warranty of 
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
    
    See the GNU General Public License for more details. You should have 
    received a copy of the GNU General Public License along with this 
    programme. If not, see <https://www.gnu.org/licenses/>. 


Purpose:
  This script builds and trains a neural network surrogate model using results 
  from LPBF single-track simulations that were generated with 
  `generate_data.py` and post-processed with "measure_W_H_D.py". The surrogate 
  maps input process parameters — laser power, scanning speed, and laser spot 
  radius — to **aggregate** melt pool characteristics computed 
  across cross-sections:
      - W_mean, W_std        
      - H_mean, H_std        
      - D_mean, D_std        
      - Porosity_mean, Porosity_std

  Definitions (consistent with the preprocessing script):
    • W (width): maximum horizontal extent within a cross-section.  
    • H (height): vertical extent of the track within a cross-section (rule 
      accounts for surface vs. internal pores as defined in the preprocessing).  
    • D (depth): vertical distance between the lowest material row and the row 
    where the maximum horizontal width occurs.

Assumptions:
  - All simulation cases listed in `parameters.txt` have been run and 
  post-processed.
  - Each `test_case_i` directory contains:
      • `cross_sections_statistics.csv`  (per cross-section records for W, H, 
                                          D, Porosity, etc.)
      • `continuous.joblib`              (boolean flag; only continuous tracks 
                                          are used)
  - Input parameters (power, speed, spot radius) are listed in 
  `parameters.txt`.
  - Required Python packages are installed: TensorFlow/Keras, NumPy, 
  scikit-learn, Matplotlib, joblib.

Method:
  1. Read input parameters from `parameters.txt`.
  2. Identify simulation cases and include only those marked as continuous via 
  `continuous.joblib`.
  3. For each valid case, load `cross_sections_statistics.csv` and compute 
  aggregate targets:
       - W_mean, W_std; H_mean, H_std; D_mean, D_std; Porosity_mean, Porosity_std
         (aggregated over all available cross-sections for that case).
  4. Assemble the dataset:
       - Features: [power, scanning speed, laser spot radius]
       - Targets:  [W_mean, W_std, H_mean, H_std, D_mean, D_std, Porosity_mean, 
                    Porosity_std]
       - Scale or normalise features and targets as appropriate for training.
  5. Build and train a feed-forward neural network using TensorFlow/Keras.
  6. Save trained artefacts:
       - Model as `NN.h5`
       - Fitted input and output scalers (saved via joblib)
  7. (Optional) Generate prediction/processing maps over the parameter space and
     plot training history and performance metrics.

Outputs:
  - `NN.h5` → trained neural network surrogate
  - `input_scaler.joblib`, `output_scaler.joblib` (or equivalent) → fitted 
     preprocessing scalers
  - Prediction/processing maps (figures)
  - Console logs containing training history and metrics

Notes:
  - Aggregates (means and standard deviations) are derived from per-section 
    entries in `cross_sections_statistics.csv`.

Authors
    Simon A. Rodriguez, University College Dublin (UCD)
    Petar Cosic, University College Dublin (UCD)
    Tom Flint, University of Manchester
    Philip Cardiff, University College Dublin (UCD)
'''

import os
import numpy as np
import random
import re
from src.functions_create_and_train_surrogate_model import *
from src.functions_measure_W_H_D import terminal

# from input_data import (SEED, MESH_DENSITY, n_epochs, 
#                        n_divisions_for_prediction, POSSIBLE_OUTPUTS)
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




import sys
from simtopc.config import load_config

config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yml"
cfg = load_config(config_path)

MESH_DENSITY = cfg.mesh_density
SEED = cfg.surrogate.seed
print("SEED is ", SEED)
n_epochs = cfg.surrogate.n_epochs
n_divisions_for_prediction = cfg.surrogate.n_divisions_for_prediction
POSSIBLE_OUTPUTS = cfg.surrogate.possible_outputs












# Seed everything 
seed_everything(SEED)

# Read the operational parameters
# parameters = np.loadtxt("./parameters.txt", skiprows=1)
parameters = np.loadtxt(cfg.parameters_file, skiprows=1)


# Count the total number of cases
number_cases = parameters.shape[0]

# Count the total number of operational parameters to evaluate
number_of_variables = parameters.shape[1]

# Check all the cases ran properly
# good_simulation_cases is a List of the cases that ran properly
good_simulation_cases = define_good_simulation_cases(MESH_DENSITY, 
                                                     number_cases)
    
# width_mean_data and width_std_data are lists W_mean and W_std from every 
# simulation
# depth_mean_data, depth_std_data are lists D_mean and D_std from every 
# simulation
# height_to_flat_mean_data, height_to_flat_std_data are lists H_mean and H_std 
# from every simulation
# porosity_mean_data, porosity_std_data are lists porosity_mean and 
# porosity_std from every simulation
width_mean_data, width_std_data, depth_mean_data, depth_std_data, \
height_to_flat_mean_data, height_to_flat_std_data, porosity_mean_data, \
porosity_std_data, cases_ran_properly_and_have_continuous_meltpool \
    = create_width_depth_height_to_flat_data(good_simulation_cases, MESH_DENSITY)


# Create and compile a Keras-based fully-connected neural network
model = create_NN(10, 3, 8)

# Count the number of useful cases, this is, cases that ran OK and have
# continuous meltpools
number_useful_cases = cases_ran_properly_and_have_continuous_meltpool.shape[0]    


# Create the scalers
x_scaler, y_scaler = create_scalers()


# # Create the data for the NN
input_data, output_data, \
parameters_valid_cases = create_input_data_and_output_data(width_mean_data, 
                                                            width_std_data, 
                                                            depth_mean_data, 
                                                            depth_std_data, 
                                                      height_to_flat_mean_data,
                                                      height_to_flat_std_data,
                                                      porosity_mean_data,
                                                      porosity_std_data,
                                                      number_useful_cases,
                    cases_ran_properly_and_have_continuous_meltpool,parameters)

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

terminal("mkdir surrogate_model")

# Save the trained neural network
model.save("surrogate_model/NN.h5")

# Save the fitted scalers
dump(x_scaler, "surrogate_model/x_scaler.joblib")
dump(y_scaler, "surrogate_model/y_scaler.joblib")

plot_history_training(history, "surrogate_model")


######### Processing map generation  ###############

# It is possible to generate a processing map, this is, a x-y figure where all 
# the x-y combinations are tested and a z variable is plotted and the colour 
# represents its magnitude. This is, it is possible to create a z-field
# over the x-y space. 

# Note that the default setup in this code assumes the parameters.txt has 
# 3 variables: speed, power, laser spot size and 8 geometric quantities are 
# estimated: W_mean, W_std, D_mean, D_std, H_mean, H_std, Porosity_mean, 
# Porosity_std. 

# To generate the processing map, 2 input variables and 1 output variables 
# must be selected. 

input_variables_for_map = [0, 1]  # This must be defined by the user. They will
                                  # be x and y in the figure. In this case, 
                                  # 0 corresponds to speed and 1 corresponds
                                  # to power
                                  
output_variables_for_map = 0 # [0]  # The index of the variable of interest in 
                                # POSSIBLE_OUTPUTS  


# generate_prediction_map(input_variables_for_map, 
#                         parameters_valid_cases, x_scaler, y_scaler, model, 
#                         POSSIBLE_OUTPUTS, x_name ="Scanning speed (m/s)", 
#                         y_name = "Power (W)")
generate_prediction_map(input_variables_for_map, parameters_valid_cases, 
                        x_scaler, y_scaler, model, POSSIBLE_OUTPUTS, 
                        "Scanning speed (m/s)", "Power (W)", 
                        n_divisions_for_prediction)


# NOTE THIS FUNCTION IS NOT FINISHED, IT IS KEPT HERE TO GENERATE THE
# CORRECT PLOT ONCE THE RULE TO DECIDE THE RULE TO DEFINE THE BOUNDARIES OF
# THE REGIMES. FOR NOW, THIS FUNCTION JUST SHOWS THE CODE THAT 
# GENERATES A SIMILAR COLOUR MAP, USING x_vals, x_vals and a synthetic
# r value, calculated as a radius.
generate_processing_map(input_variables_for_map, parameters_valid_cases, n_divisions_for_prediction)

terminal("mkdir images_from_predictions")
terminal("mv *png images_from_predictions")

print("Thanks for using this software.")