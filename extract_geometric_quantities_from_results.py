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
from joblib import dump, load
import random
import re
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.preprocessing import MinMaxScaler
from itertools import combinations
# import importlib

# Seed everything 
# seed_everything(SEED)

# source the correct openfoam, based on the system and OF version
hostname, run_address, OF_LOCATION = set_environment_variables()

# Select the proper base case
BASE_CASE_NAME = set_base_case_name()

# Read the operational parameters
parameters = np.loadtxt("./parameters.txt", skiprows=1)

# Count the total number of cases
number_cases = parameters.shape[0]

# Count the total number of operational parameters to evaluate
# number_of_variables = parameters.shape[1]

# Create the simulation cases, locally        
# create_simulation_cases(number_cases, BASE_CASE_NAME, parameters)


# Unzip the results
for i in range(number_cases):  
    name_new_folder = MESH_DENSITY + "/test_case_" + str(i + 1)
    terminal("unzip " + name_new_folder + ".zip -d " + MESH_DENSITY + "/")
    terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && pvpython postproc2.py"')
    terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && pvpython postproc3.py"')
    terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && python quantitiesFromMeltpool.py"')



# # Calculate results (width, depth, etc)
# for i in range(number_cases):
#     name_new_folder = MESH_DENSITY + "/test_case_" + str(i + 1)
#     terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && pvpython postproc2.py"')
#     terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && pvpython postproc3.py"')
#     terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && python quantitiesFromMeltpool.py"')


print("Data generation completed.")

exit()


# # Check all the cases ran properly
# good_simulation_cases = [] # List of the cases that ran properly
# for i in range(1, number_cases + 1):
#     name_new_folder = MESH_DENSITY + "/test_case_" + str(i)
#     files_in_folder_i = os.listdir("./" + name_new_folder)

#     # Verificar si "finished.txt" está en la lista
#     if 'finished.txt' in files_in_folder_i:
#         good_simulation_cases.append(i)
#     #     pass
#     # else:
#     #     print(name_new_folder + " did not run properly")
#     #     print("Check the simulations that failed")
#     #     break
# if (len(good_simulation_cases) < number_cases):
#     print("Some simulation cases did not run properly.")


# width_data, depth_data, height_to_flat_data, \
# cases_ran_properly_and_have_continuous_meltpool = \
#     create_width_depth_height_to_flat_data(good_simulation_cases)


# # Create and compile the neural network    
# model = create_NN(10, 3, 3)

# # Count the number of useful cases, this is, cases that ran OK and have
# # continuous meltpools
# number_useful_cases = cases_ran_properly_and_have_continuous_meltpool.shape[0]


# # Create the scalers
# x_scaler, y_scaler = create_scalers()


# # # Create the data for the NN
# input_data, output_data, parameters_valid_cases = \
#     create_input_data_and_output_data(width_data, depth_data, 
#                                       height_to_flat_data, number_useful_cases, 
#                                cases_ran_properly_and_have_continuous_meltpool,
#                                parameters)

# # Fit the scalers
# fit_scalers(x_scaler, y_scaler, input_data, output_data)


# # Scale the input and output
# input_data_scaled, output_data_scaled = scale_data(x_scaler, y_scaler, 
#                                                    input_data, output_data)


# # Make input and output data 3D for the NN
# input_data_scaled = input_data_scaled[:, np.newaxis, :]
# output_data_scaled = output_data_scaled[:, np.newaxis, :]

# # Train the ML model
# history = model.fit(input_data_scaled, output_data_scaled, epochs = n_epochs, 
#                     validation_split = 0.01)


# # x_for_predictions is a list. Every element of the list is a numpy array that 
# # contains all the elements that will be used for training. For instance, 
# # if the parameters.txt file has m columns, x_for_predictions will have 
# # m elements. Each element is a numpy array of all the values that variable 
# # will take at predicion time. 

# # 
# x_intervals = []
# for i in range(parameters_valid_cases.shape[1]):
#     xi_values = np.linspace(min(parameters_valid_cases[:, i]), 
#                             max(parameters_valid_cases[:, i]), 
#                             n_divisions_for_prediction)
#     x_intervals.append(xi_values)
    

# grids = np.meshgrid(*x_intervals, indexing='ij')  # 'ij' preserves the order

# # To reshape into a 2D list of parameter combinations
# x_predict = np.stack(grids, axis=-1).reshape(-1, len(x_intervals))

# x_predict_scaled = x_scaler.transform(x_predict)
# y_predict_scaled = model.predict(x_predict_scaled[:, np.newaxis, :])
# y_predict = y_scaler.inverse_transform(y_predict_scaled.reshape([y_predict_scaled.shape[0], 
#                                                                  y_predict_scaled.shape[2]]))



# n_input_variables = parameters_valid_cases.shape[1]
# n_output_variables = len(POSSIBLE_OUTPUTS)
# n_input_variables_that_will_be_fixed = parameters_valid_cases.shape[1] - 2 # The
# # number 2 here is because there will always be 2 variables to plot from the 
# # input. The other varialbes will be fixed at some level for plotting


# input_variables_for_map = [0, 1]  # This must be defined by the user. They will
#                                   #be x and y in the figure
# output_variables_for_map = 1 # [0]  # The index of the variable of interest in 
#                                 # POSSIBLE_OUTPUTS  
                                

# x_vals = np.linspace(min(parameters_valid_cases[:, input_variables_for_map[0] ]), 
#                      max(parameters_valid_cases[:, input_variables_for_map[0] ]), 
#                      n_divisions_for_prediction)
# y_vals = np.linspace(min(parameters_valid_cases[:, input_variables_for_map[1] ]), 
#                      max(parameters_valid_cases[:, input_variables_for_map[1] ]), 
#                      n_divisions_for_prediction)
# # z_vals = np.linspace(min(np.unique(parameters_valid_cases[:, 2])), 
# #                      max(np.unique(parameters_valid_cases[:, 2])), 
# #                      n_divisions_for_prediction)
# # z_vals = parameters_valid_cases[:, 2][0]






# input_combinations = list(combinations(range(parameters_valid_cases.shape[1]), 2))  # pares de entradas
# output_indices = list(range(n_output_variables))  # índices de salida



                            






# x, y = np.meshgrid(x_vals, y_vals)

# # Reshape x and y to make predictions with the NN
# x_for_map = x.reshape((x.shape[0] * x.shape[0], 1, 1))
# y_for_map = y.reshape((y.shape[0] * y.shape[0], 1, 1))
# z_for_map = np.zeros(x_for_map.shape)
# z_for_map[:, :] =  parameters_valid_cases[:, 2][output_variables_for_map]


# x_for_predictions = np.concatenate((x_for_map, y_for_map, z_for_map), axis = 2)
# x_for_predictions_scaled = x_scaler.transform(x_for_predictions.reshape([x_for_predictions.shape[0],
#                                                                          x_for_predictions.shape[2]] ))
# y_predictions_scaled = model.predict(x_for_predictions_scaled[:, np.newaxis, :])
# y_predictions = y_scaler.inverse_transform(y_predictions_scaled.reshape([y_predictions_scaled.shape[0], 
#                                                                          y_predictions_scaled.shape[2]]))



# # # Make predictions
# # x_training = np.concatenate((x_for_map, y_training), axis = 2)
# # x_training = x_training.reshape((x_for_map.shape[0], 1, 2))
# # y_predicted = model.predict(x_training)




# plt.figure(figsize=(8, 6))
# plt.pcolormesh(x_for_predictions[:, :, 0].reshape([n_divisions_for_prediction, 
#                                                    n_divisions_for_prediction]), 
#                x_for_predictions[:, :, 1].reshape([n_divisions_for_prediction, 
#                                                    n_divisions_for_prediction]), 
#                y_predictions[:, output_variables_for_map].reshape([n_divisions_for_prediction, 
#                                                    n_divisions_for_prediction]), shading='auto')
# plt.colorbar(label='Predicted Width')  # O cualquier unidad/etiqueta apropiada
# plt.xlabel('Input Variable 0')
# plt.ylabel('Input Variable 1')
# plt.title('Color Map of Predicted Output')
# plt.tight_layout()
# plt.show()





# # # These z-values should be replaced with the ones from the model once it has been trained with simulation results, i am doing it with this for now for testing purposes
# # distances = (x**2 + y**2)**0.5

# x, y = np.meshgrid(x_vals, x_vals)

# # 1. Crear valor simulado
# r = np.sqrt(x**2 + y**2)  # aumenta con x e y

# distances = (x**2 + y**2)**0.5
# z = np.zeros(distances.shape)
# z[distances < 1.2] = 0
# z[(distances >= 1.2) & (distances <= 2)] = 1
# z[distances > 2] = 2


# z = z.astype(int)


# # Convertir a enteros
# # z = z.astype(int)

# cmap = ListedColormap(['red', 'green', 'blue'])


# plt.figure(figsize=(8, 6))
# plt.pcolormesh(x, y, z, cmap=cmap, shading='auto')
# plt.xlabel('Scanning speed (mm/s)')
# plt.ylabel('Laser Power (W)')
# plt.title('Processing map')
# cbar = plt.colorbar(ticks=[0.5, 1.5, 2.5])
# cbar.ax.set_yticklabels(['Lack of fusion', 'Optimol', 'Overfusion'])
# plt.tight_layout()
# plt.show()


# exit()


# # plt.figure(figsize=(8, 6))
# # plt.pcolormesh(x, y, z, cmap=cmap, shading='auto')
# # plt.xlabel('Scanning speed (mm/s)')
# # plt.ylabel('Laser Power (W)')
# # plt.title('Processing map')
# # cbar = plt.colorbar(ticks=[0.5, 1.5, 2.5])
# # cbar.ax.set_yticklabels(['Lack of fusion', 'Optimol', 'Overfusion'])
# # plt.tight_layout()
# # plt.grid()
# # plt.show()


# exit()









# n_div = len(np.unique(x_predict[:, 0]))  # asumiendo cuadrícula cuadrada
# # Reconvertir a grilla para graficar
# X = x_predict[:, 0].reshape(n_divisions_for_prediction, n_divisions_for_prediction)

# Y = x_predict[:, 1].reshape(n_divisions_for_prediction, n_divisions_for_prediction)


# # Extraer y reorganizar cada salida
# Z_width = y_predict[:, 0].reshape(n_divisions_for_prediction, n_divisions_for_prediction)
# # Z_depth = y_predict[:, 1].reshape(n_div, n_div)
# # Z_height = y_predict[:, 2].reshape(n_div, n_div)

# plt.figure(figsize=(8, 6))
# mesh = plt.pcolormesh(X, Y, Z, shading='auto', cmap='viridis')
# plt.xlabel('Speed')
# plt.ylabel('Power')
# plt.title(title)
# plt.colorbar(mesh, label=label)
# plt.tight_layout()
# plt.show()
# plt.close()


















    
    


# # print(grid_points.shape)  # (N, D) shape where N is total points, D is number of variables

    

# # Create the x_for_predictions
# x_predict_short = np.zeros([n_divisions_for_prediction, len(x_for_predictions)])
# for i in range(parameters_valid_cases.shape[1]):
#     x_predict_short[:, i] = x_for_predictions[i]


# x_predict_extended = []

# # for i in range(parameters_valid_cases.shape[1]):




# # # Scale x_predict
# # x_predict_scaled = x_scaler.transform(x_predict)

# # # Perform the predictions
# # y_predict_scaled = model.predict(x_predict_scaled[:, np.newaxis, :])


# # # Scaled the predictions back to their original scales
# # y_predict = y_scaler.inverse_transform(y_predict_scaled.reshape([y_predict_scaled.shape[0], y_predict_scaled.shape[2]]))















# # x_for_predictions = np.linspace(min(parameters_valid_cases[:, 1]), max(parameters_valid_cases[:, 1]), 50)





# # ######## I probably do not need the code in this section ############
# # # Make predicions
# # # points_distance_to_origin = (parameters[:, 0]**2 + parameters[:, 1]**2)**0.5 
# # points_distance_to_origin = (parameters_valid_cases[:, 0]**2 + parameters_valid_cases[:, 1]**2)**0.5 
# # minimum_distance = min(points_distance_to_origin) # This line is just for reference
# # minimum_distance_index = np.argmin(points_distance_to_origin)

# # maximum_distance = max(points_distance_to_origin) # This line is just for reference
# # maximum_distance_index = np.argmax(points_distance_to_origin)
# # ###########################################################################


# # # Generate the plot
# # # x_vals = np.linspace(min(parameters[:, 1]), max(parameters[:, 1]), 50)
# # # y_vals = np.linspace(min(parameters[:, 0]), max(parameters[:, 1]), 50)
# # x_vals = np.linspace(min(parameters_valid_cases[:, 1]), max(parameters_valid_cases[:, 1]), 50)
# # y_vals = np.linspace(min(parameters_valid_cases[:, 0]), max(parameters_valid_cases[:, 1]), 50)

# # x, y = np.meshgrid(x_vals, y_vals)


# # # Reshape x and y to make predictions with the NN
# # x_training = x.reshape((x.shape[0] * x.shape[0], 1))
# # y_training = y.reshape((y.shape[0] * y.shape[0], 1))

# # # Make predictions
# # x_training = np.concatenate((x_training, y_training), axis = 1)
# # x_training = x_training.reshape((x_training.shape[0], 1, 2))
# # y_predicted = model.predict(x_training)

# # width_predicted = y_predicted[:, :, 0].reshape((int(y_predicted.shape[0]**0.5), int(y_predicted.shape[0]**0.5)))
# # depth_predicted = y_predicted[:, :, 1].reshape((int(y_predicted.shape[0]**0.5), int(y_predicted.shape[0]**0.5)))
# # height_to_flat_predicted = y_predicted[:, :, 2].reshape((int(y_predicted.shape[0]**0.5), int(y_predicted.shape[0]**0.5)))


# # # These z-values should be replaced with the ones from the model once it has been trained with simulation results, i am doing it with this for now for testing purposes
# # distances = (x**2 + y**2)**0.5
# # z = np.zeros(distances.shape)
# # z[distances < 1.8] = 0
# # z[(distances >= 1.8) & (distances <= 2.5)] = 1
# # z[distances > 2.5] = 2



# # cmap = ListedColormap(['red', 'green', 'blue'])


# # plt.figure(figsize=(8, 6))
# # plt.pcolormesh(x, y, z, cmap=cmap, shading='auto')
# # plt.xlabel('Scanning speed (mm/s)')
# # plt.ylabel('Laser Power (W)')
# # plt.title('Processing map')
# # cbar = plt.colorbar(ticks=[0.5, 1.5, 2.5])
# # cbar.ax.set_yticklabels(['Lack of fusion', 'Optimol', 'Overfusion'])
# # plt.tight_layout()
# # plt.show()




















