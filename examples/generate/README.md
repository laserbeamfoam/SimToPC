# Generate

## Purpose

The `generate` mode is used to prepare and execute LPBF simulation cases as part of the simulation-to-characterisation workflow implemented in SimToPC.

Starting from a predefined base case, this mode modifies the simulation setup according to user-specified operational parameters and manages the execution of the resulting cases.

The base case is selected from the directory corresponding to the user-defined `mesh_density` specified in the `config.yml` file.

In this tutorial, the selected mesh density is `COARSE`, and the corresponding base case is located in:

`COARSE/base_case_of2412`



## Base case template

At present, the base case template must be provided by the user.

The base case directory follows the naming convention:

base_case_of2412

where:
- `base_case` denotes the simulation template, and
- `of2412` indicates the OpenFOAM version used, which is also specified by the user in the `config.yml` file (OpenFOAM v2412 in this case).


## Operational parameters

The operational parameters used to generate simulation cases are defined by the user in a text file named `parameters.txt`, located in the directory containing this tutorial.

For this tutorial, the `parameters.txt` file defines the following combinations of scanning speed, laser power, and spot size:

```text
Scanning Speed (m/s) | Power (W)  | Spot size (m)   
1                         150             80e-6
1.5                       150             80e-6
2                         150             80e-6
1                         200             80e-6
1.5                       200             80e-6
2                         200             80e-6
1                         250             80e-6
1.5                       250             80e-6
2                         250             80e-6
0.5                       150             80e-6
0.5                       200             80e-6
0.5                       250             80e-6
1                         300             80e-6
1.5                       300             80e-6
2                         300             80e-6
```

Each row corresponds to a unique combination of operational parameters, resulting in a total of twelve simulation cases for this tutorial.



## Basic usage

Before running SimToPC, ensure that the Python environment in which the package was installed is active, as described in the main repository `README.md`.

The `generate` mode is invoked through the SimToPC command-line interface:

```bash
simtopc generate config.yml
```

When executed, SimToPC reads the `parameters.txt` file and automatically modifies the base case template to create one simulation case for each parameter combination. The required OpenFOAM input files are updated programmatically according to the specified operational parameters.



## Outputs

The `generate` mode creates one simulation directory per parameter combination.

For this tutorial, twelve simulation case directories are created within the selected `mesh_density` directory (`COARSE/`). Each case is stored in a folder named according to the convention:

`test_case_i`, where `i` denotes the index of the parameter combination being evaluated.

Each directory contains the complete OpenFOAM case setup and the corresponding raw simulation outputs required for subsequent post-processing using the `measure` mode.


## Notes

This mode is intended for advanced use and typically requires access to an OpenFOAM-based LPBF solver and a suitable execution environment.

The user is responsible for ensuring that the provided base case is valid and runs correctly in the target execution environment (e.g. that required scripts such as `Allrun` execute successfully on the chosen HPC system).

The user is also responsible for ensuring that the target execution environment can be accessed without interactive authentication (e.g. passwordless access), as required for automated execution.

In this tutorial, simulations are executed on an HPC system at University College Dublin (UCD) named `Xenosim`. The corresponding execution settings are defined in the file:

simtopc/input_files/running_on_inp.py

The execution environment is selected via the `running_on` entry in the `config.yml` file. For this tutorial, the configuration for `Xenosim` contains:

```python
hostname    = "xenosim"  
run_address = "/home/simon/run/"  
OF_LOCATION = "$HOME/OpenFOAM/OpenFOAM-v2412/etc/bashrc"
```

These settings are provided as an example and must be adapted by the user for their own execution environment.

For the parameter set used in this tutorial, individual simulations are computationally expensive. Using the settings described above, a single case typically requires several hours of wall-clock time (approximately 5 hours using 80 CPU cores).

For this reason, the `generate` mode is not executed as part of the tutorial workflow. Instead, the simulation results corresponding to these cases are provided with the repository and are used as input for the tutorials associated with the `measure` and `surrogate` modes.
