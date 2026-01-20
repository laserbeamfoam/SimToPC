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
  Implementation of the melt-pool measurement stage in the SimToPC
  workflow.

  This module orchestrates the post-processing of completed simulation
  cases to extract melt-pool geometry and related metrics. It manages
  the preparation of case-specific inputs, the execution of auxiliary
  post-processing scripts, and the aggregation of geometry data into
  structured outputs.

  The implementation is designed to be solver-agnostic at the workflow
  level, while relying on solver-specific helper scripts for field
  extraction.

Assumptions
  - Simulation cases have been successfully completed prior to execution
  - Required OpenFOAM and pvpython environments are available
  - Case directory structures follow the conventions used by SimToPC
  - Measurement parameters are provided via a validated configuration
    object

Authors
  Simon A. Rodriguez, University College Dublin (UCD)
  Alojz Ivankovic, University College Dublin (UCD)
  Petar Cosic, University College Dublin (UCD)
  Tom Flint, University of Manchester (UoM)
  Philip Cardiff, University College Dublin (UCD)
"""


from __future__ import annotations
from pathlib import Path
import numpy as np
import shutil
from importlib import resources as _stdlib_resources

if hasattr(_stdlib_resources, "files") and hasattr(_stdlib_resources, 
                                                   "as_file"):
    resources = _stdlib_resources
else:
    import importlib_resources as resources  # type: ignore

import json


def copy_measure_resources(case_dir: Path) -> None:
    """
    Copy helper scripts into a case directory from packaged resources.
    This avoids relying on a repo-local 'src/' folder and works after 
    pip install.
    """
    pkg = "simtopc.resources.src"
    filenames = [
        "extract_meltpool.py",
        "extract_x_z_slice_meltpool.py",
        "extract_y_z_slice_meltpool.py",
        "functions.py",
    ]

    for fname in filenames:
        with resources.as_file(resources.files(pkg) / fname) as src_path:
            shutil.copy(src_path, case_dir / fname)

from simtopc.measure.legacy_funcs import (set_environment_variables,
                                          terminal, 
                                          calculate_geometry_full_meltpool,
                                          )

def run_measure_cases(cfg_all, measure_cfg, config_path: Path) -> None:
    # source the correct OpenFOAM, based on the system and OF version
    hostname, run_address, OF_LOCATION = set_environment_variables(
                                                            cfg_all.running_on)

    # Read the operational parameters
    parameters = np.loadtxt(cfg_all.parameters_file, skiprows=1)
    number_cases = parameters.shape[0]

    for i in range(number_cases):
        name_new_folder = cfg_all.mesh_density + "/test_case_" + str(i + 1)

        case_dir = Path(name_new_folder)
        case_dir.mkdir(parents=True, exist_ok=True)

        payload = {
            "Y_COORD_BEGIN_TRACK": float(measure_cfg.y_begin),
            "Y_COORD_END_TRACK": float(measure_cfg.y_end),
        }
      
        (case_dir / "measure_inputs.json").write_text(json.dumps(payload, 
                                                                     indent=2))

        print(f"\n Measuring geometry-based quantities for test_case_{i+1}")
        copy_measure_resources(Path(name_new_folder))
        laser_radius_i = parameters[i, 2] / 2
        print(f"\n Extracting meltpool geometry")
        terminal(f'bash -lc "source {OF_LOCATION} && cd {name_new_folder} '
                 '&& pvpython extract_meltpool.py"'
                )

        calculate_geometry_full_meltpool(name_new_folder, laser_radius_i, 
                                         measure_cfg, 
                                       CSV_3D=name_new_folder + "/meltpool.csv"
                                       )

        terminal(f'cd {name_new_folder} && mkdir images_full_meltpool')
        terminal(f'cd {name_new_folder} && mv *png images_full_meltpool/')

        print(f"\nFinished measuring geometry-based quantities "
              f"for test_case_{i + 1}\n")

    print("Geometry measurement finished.")