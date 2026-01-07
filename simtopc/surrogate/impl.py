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
# import input_data
# from input_data import *
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

from pathlib import Path

def terminal(command):
    os.system(command)

def create_NN(n_nodes, n_input_variables, n_output_variables):
    # Set the neural network up
    model = Sequential()
    model.add(Dense(units = n_nodes, 
                    kernel_initializer = 'he_normal', 
                    activation = 'relu', input_shape = (None, 
                                                        n_input_variables)))
    model.add(Dense(units = n_output_variables, 
                    kernel_initializer = 'he_normal', activation = 'linear'))
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

           
# def create_width_depth_height_to_flat_data(good_simulation_cases):
def create_width_depth_height_to_flat_data(good_simulation_cases, mesh_density):

    # Assemble the training set
    width_mean_data = []
    width_std_data = []
    depth_mean_data = []
    depth_std_data = []
    height_to_flat_mean_data = []
    height_to_flat_std_data = []
    porosity_mean_data = []
    porosity_std_data = []
    
    cases_ran_properly_and_have_continuous_meltpool = []
    for i in good_simulation_cases:
        name_new_folder = mesh_density + "/test_case_" + str(i)
        # meltpool_i_is_cotinuous = load("./" + name_new_folder + 
        #                                "/continuous.joblib")
        meltpool_i_is_cotinuous = load(str(Path(name_new_folder) / "continuous.joblib"))
        
        if (meltpool_i_is_cotinuous):
            # Read the data
            # df = pd.read_csv("./" + name_new_folder + 
            #                  "/cross_sections_statistics.csv")
            df = pd.read_csv(str(Path(name_new_folder) / "cross_sections_statistics.csv"))
            width_mean = np.mean(df["width"].to_numpy())
            width_std = np.std(df["width"].to_numpy())
            depth_mean = np.mean(df["depth"].to_numpy())
            depth_std = np.std(df["depth"].to_numpy())
            height_to_flat_mean = np.mean(df["height"].to_numpy())
            height_to_flat_std = np.std(df["height"].to_numpy())
            porosity_mean = np.mean(df["porosity_at_iy"].to_numpy())
            porosity_std = np.std(df["porosity_at_iy"].to_numpy())            
            
            
            width_mean_data.append(width_mean)
            width_std_data.append(width_std)
            depth_mean_data.append(depth_mean)
            depth_std_data.append(depth_std)
            height_to_flat_mean_data.append(height_to_flat_mean)
            height_to_flat_std_data.append(height_to_flat_std)
            porosity_mean_data.append(porosity_mean)
            porosity_std_data.append(porosity_std)
            cases_ran_properly_and_have_continuous_meltpool.append(i)

    cases_ran_properly_and_have_continuous_meltpool = np.array(
                               cases_ran_properly_and_have_continuous_meltpool
                                                              )
    return width_mean_data, width_std_data, depth_mean_data, depth_std_data, \
           height_to_flat_mean_data, height_to_flat_std_data, \
           porosity_mean_data, porosity_std_data, \
           cases_ran_properly_and_have_continuous_meltpool
           
           
           

def seed_everything(SEED):
    random.seed(SEED)
    np.random.seed(SEED)
    tf.random.set_seed(SEED)
    

def create_input_data_and_output_data(width_mean_data, width_std_data, 
                                       depth_mean_data, depth_std_data, 
                                       height_to_flat_mean_data, 
                                       height_to_flat_std_data, 
                                       porosity_mean_data, porosity_std_data,
                                       number_useful_cases, 
                               cases_ran_properly_and_have_continuous_meltpool,
                                      parameters):
    
    width_mean_data = np.array(width_mean_data).reshape((number_useful_cases, 
                                                         1, 1))
    width_std_data = np.array(width_std_data).reshape((number_useful_cases, 
                                                       1, 1))
    depth_mean_data = np.array(depth_mean_data).reshape((number_useful_cases, 
                                                         1, 1))
    depth_std_data = np.array(depth_std_data).reshape((number_useful_cases, 
                                                       1, 1))
    height_to_flat_mean_data = np.array(height_to_flat_mean_data).reshape(
                                                    (number_useful_cases, 1, 1)
                                                                         )
    height_to_flat_std_data = np.array(height_to_flat_std_data).reshape(
                                                   (number_useful_cases, 1, 1)
                                                                       )
    porosity_mean_data = np.array(porosity_mean_data).reshape(
                                                   (number_useful_cases, 1, 1)
                                                             )
    porosity_std_data = np.array(porosity_std_data).reshape(
                                                   (number_useful_cases, 1, 1)
                                                           )

    parameters_valid_cases = parameters[
                             cases_ran_properly_and_have_continuous_meltpool-1]
    input_data = parameters_valid_cases.reshape((number_useful_cases, 1, 
                                              parameters_valid_cases.shape[1]))
    output_data = np.concatenate((width_mean_data, width_std_data, 
                                  depth_mean_data, depth_std_data, 
                                  height_to_flat_mean_data, 
                                  height_to_flat_std_data, porosity_mean_data, 
                                  porosity_std_data), axis = 2)
    
    return input_data, output_data, parameters_valid_cases
    

def define_good_simulation_cases(mesh_density, number_cases):
    good_simulation_cases = [] # List of the cases that ran properly
    for i in range(1, number_cases + 1):
        name_new_folder = mesh_density + "/test_case_" + str(i)
        # files_in_folder_i = os.listdir("./" + name_new_folder)
        # files_in_folder_i = os.listdir(name_new_folder)
        files_in_folder_i = os.listdir(str(Path(name_new_folder)))

    
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

# def generate_x_y_levels_for_predictions(parameters_valid_cases, x_ind, y_ind):
def generate_x_y_levels_for_predictions(parameters_valid_cases, x_ind, y_ind, n_divisions_for_prediction):

    x_vals = np.linspace(min(parameters_valid_cases[:, x_ind]), 
                         max(parameters_valid_cases[:, x_ind]), 
                         n_divisions_for_prediction)
    y_vals = np.linspace(min(parameters_valid_cases[:, y_ind]), 
                         max(parameters_valid_cases[:, y_ind]), 
                         n_divisions_for_prediction)
    
    return x_vals, y_vals
    

# def generate_prediction_map(input_variables_for_map, 
#                             parameters_valid_cases, x_scaler, y_scaler, model,
#                             possible_outputs, x_name, y_name):
def generate_prediction_map(input_variables_for_map, 
                            parameters_valid_cases, x_scaler, y_scaler, model,
                            possible_outputs, x_name, y_name, n_divisions_for_prediction):

    
    for i in range(len(possible_outputs)):
        # Generate the x and y values that will be used in th predicions 
        x_vals, y_vals = generate_x_y_levels_for_predictions(parameters_valid_cases, 
                                                      input_variables_for_map[0],
                                                      input_variables_for_map[1], n_divisions_for_prediction)
    
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
                                                            n_divisions_for_prediction]), shading='auto', cmap='jet')
        plt.colorbar(label="Predicted " + possible_outputs[i] + " (m)")
        plt.xlabel(x_name)
        plt.ylabel(y_name)
        plt.title("Predictions using the NN")
        plt.tight_layout()
        # plt.show()
        plt.savefig(possible_outputs[i]+ "_predictions.png")
    

# def generate_prediction_map(input_variables_for_map, 
#                             parameters_valid_cases, x_scaler, y_scaler, model,
#                             possible_outputs, x_name, y_name):
    
#     for i in range(len(possible_outputs)):
#         # 1) Generate the x and y values that will be used in the predictions 
#         x_vals, y_vals = generate_x_y_levels_for_predictions(
#             parameters_valid_cases, 
#             x_ind=input_variables_for_map[0],
#             y_ind=input_variables_for_map[1]
#         )
    
#         # 2) Grid for map
#         X_grid, Y_grid = np.meshgrid(x_vals, y_vals)
#         n_points = X_grid.size
    
#         # 3) Prepare NN input
#         x_for_map = X_grid.reshape((n_points, 1, 1))
#         y_for_map = Y_grid.reshape((n_points, 1, 1))
#         z_for_map = np.zeros_like(x_for_map)
#         z_for_map[:, :] = parameters_valid_cases[:, 2][i]
    
#         x_for_predictions = np.concatenate((x_for_map, y_for_map, z_for_map), axis=2)

#         x_for_predictions_scaled = x_scaler.transform(
#             x_for_predictions.reshape([x_for_predictions.shape[0],
#                                        x_for_predictions.shape[2]])
#         )
#         y_predictions_scaled = model.predict(x_for_predictions_scaled[:, np.newaxis, :])
#         y_predictions = y_scaler.inverse_transform(
#             y_predictions_scaled.reshape([y_predictions_scaled.shape[0],
#                                           y_predictions_scaled.shape[2]])
#         )

#         # 4) Reshape predictions back into grid
#         Z_grid = y_predictions[:, i].reshape(X_grid.shape)

#         # 5) ---- MASK THE UNSAFE RECTANGLE ----
#         # rectangle defined by:
#         # speed in [1.75, 2.25]
#         # power in [125, 175]
#         invalid_mask = (
#             (X_grid >= 1.75) & (X_grid <= 2.25) &
#             (Y_grid >= 125.0) & (Y_grid <= 175.0)
#         )

#         Z_masked = np.ma.array(Z_grid, mask=invalid_mask)

#         # 6) Plot
#         plt.figure(figsize=(8, 6))
#         pcm = plt.pcolormesh(
#             X_grid,
#             Y_grid,
#             Z_masked,
#             shading='auto',
#             cmap='jet'
#         )
#         plt.colorbar(pcm, label="Predicted " + possible_outputs[i] + " (m)")
#         plt.xlabel(x_name)
#         plt.ylabel(y_name)
#         plt.title("Predictions using the NN")
#         plt.tight_layout()
#         plt.savefig(possible_outputs[i] + "_predictions.png")







def generate_processing_map(input_variables_for_map, parameters_valid_cases, n_divisions_for_prediction):
    # NOTE THIS FUNCTION IS NOT FINISHED, IT IS KEPT HERE TO GENERATE THE
    # CORRECT PLOT ONCE THE RULE TO DECIDE THE RULE TO DEFINE THE BOUNDARIES OF
    # THE REGIMES. FOR NOW, THIS FUNCTION JUST SHOWS THE CODE THAT 
    # GENERATES A SIMILAR COLOUR MAP, USING x_vals, x_vals and a synthetic
    # r value, calculated as a radius.
    x_vals, y_vals = generate_x_y_levels_for_predictions(parameters_valid_cases, 
                                                  input_variables_for_map[0],
                                                  input_variables_for_map[1], n_divisions_for_prediction)

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
    

def plot_history_training(history, destination_file):
    # Plot loss vs. epochs
    plt.plot(history.history['loss'], label='Training loss')
    plt.plot(history.history['val_loss'], label='Validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    # plt.show()
    plt.savefig(destination_file + "/loss_vs_iterations.png", dpi=300)  # saves as PNG (high res)
    