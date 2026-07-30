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
import pandas as pd


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
                                          _measure_aux_dir,
                                          _measure_work_dir,
                                          )


MEASURE_WORK_FILENAMES = (
    "extract_meltpool.py",
    "extract_x_z_slice_meltpool.py",
    "extract_y_z_slice_meltpool.py",
    "functions.py",
)


def archive_measure_work_files(case_dir: Path) -> None:
    work_dir = _measure_work_dir(str(case_dir))
    for filename in MEASURE_WORK_FILENAMES:
        file_path = case_dir / filename
        if file_path.exists():
            file_path.replace(work_dir / filename)

    for clip_path in sorted(case_dir.glob("Clip*.png")):
        clip_path.replace(work_dir / clip_path.name)


def _read_openfoam_scalar_internal_field(path: Path) -> list[float]:
    lines = path.read_text().splitlines()
    start = None
    count = None
    for i, line in enumerate(lines):
        if line.strip().isdigit():
            count = int(line.strip())
            start = i + 2
            break
    if start is None or count is None:
        raise ValueError(f"Could not parse OpenFOAM scalar field: {path}")
    values = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped == ")":
            break
        if stripped:
            values.append(float(stripped))
    if len(values) != count:
        raise ValueError(f"Expected {count} values in {path}, found {len(values)}")
    return values


def extract_cell_centres_meltpool(case_dir: Path, cell_size: float) -> None:
    """Write meltpool.csv from occupied OpenFOAM cell centres.

    This is used by controlled manufactured tests where the reference
    geometry is prescribed as a mesh-cell mask rather than as interpolated
    point data.
    """
    time_dirs = sorted(
        [p for p in case_dir.iterdir() if p.is_dir() and p.name not in {"0", "constant", "system", "measure_aux", "measure_results", "measure_work"}],
        key=lambda p: float(p.name),
    )
    if not time_dirs:
        raise FileNotFoundError(f"No time directory found in {case_dir}")
    time_dir = time_dirs[-1]
    xs = _read_openfoam_scalar_internal_field(time_dir / "Cx")
    ys = _read_openfoam_scalar_internal_field(time_dir / "Cy")
    zs = _read_openfoam_scalar_internal_field(time_dir / "Cz")
    alpha = _read_openfoam_scalar_internal_field(time_dir / "cellAlpha.material")
    half_cell = 0.5 * cell_size
    rows = [
        (x - half_cell, y - half_cell, z - half_cell)
        for x, y, z, a in zip(xs, ys, zs, alpha)
        if a > 0.5
    ]
    pd.DataFrame(rows, columns=["Points_0", "Points_1", "Points_2"]).to_csv(
        case_dir / "meltpool.csv",
        index=False,
    )

def run_measure_cases(cfg_all, measure_cfg, config_path: Path) -> None:
    # source the correct OpenFOAM, based on the system and OF version
    # hostname, run_address, OF_LOCATION = set_environment_variables(
    #                                                         cfg_all.running_on)
    hostname, run_address, OF_LOCATION = set_environment_variables(cfg_all.environment)


    # Read the operational parameters
    parameters = np.atleast_2d(np.loadtxt(cfg_all.parameters_file, skiprows=1))
    number_cases = parameters.shape[0]

    for i in range(number_cases):
        name_new_folder = cfg_all.mesh_density + "/test_case_" + str(i + 1)

        case_dir = Path(name_new_folder)
        case_dir.mkdir(parents=True, exist_ok=True)

        payload = {
            "Y_COORD_BEGIN_TRACK": float(measure_cfg.y_begin),
            "Y_COORD_END_TRACK": float(measure_cfg.y_end),
        }

        aux_dir = _measure_aux_dir(name_new_folder)
        (case_dir / "measure_inputs.json").write_text(json.dumps(payload,
                                                                 indent=2))

        print(f"\n Measuring geometry-based quantities for test_case_{i+1}")
        copy_measure_resources(Path(name_new_folder))
        laser_radius_i = parameters[i, 2] / 2
        print(f"\n Extracting meltpool geometry")
        if measure_cfg.extraction_mode == "cell_centres":
            extract_cell_centres_meltpool(case_dir, measure_cfg.cell_size)
        else:
            terminal(f'bash -lc "source {OF_LOCATION} && cd {name_new_folder} '
                     '&& pvpython extract_meltpool.py"'
                    )

        archive_measure_work_files(case_dir)

        meltpool_csv = case_dir / "meltpool.csv"
        if meltpool_csv.exists():
            meltpool_csv.replace(aux_dir / "meltpool.csv")
        measure_inputs_json = case_dir / "measure_inputs.json"
        if measure_inputs_json.exists():
            measure_inputs_json.replace(aux_dir / "measure_inputs.json")

        calculate_geometry_full_meltpool(name_new_folder, laser_radius_i, 
                                         measure_cfg, 
                                       CSV_3D=str(aux_dir / "meltpool.csv")
                                       )

        print(f"\nFinished measuring geometry-based quantities "
              f"for test_case_{i + 1}\n")

    print("Geometry measurement finished.")
