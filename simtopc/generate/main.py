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
  Entry point for the simulation-case generation stage of the SimToPC
  workflow.

  This module implements the logic executed by the `simtopc generate`
  command. It orchestrates the creation of simulation cases from a user
  configuration file, updates solver input files with process parameters,
  and manages the execution of simulations either locally or on remote
  HPC systems.

  The module coordinates higher-level workflow steps while delegating
  low-level operations (file manipulation, job submission, monitoring)
  to legacy helper utilities.

Assumptions
  - This module is invoked via the SimToPC command-line interface
  - The user provides a valid SimToPC configuration file (YAML)
  - Simulation cases are based on an existing OpenFOAM base case
  - Local or remote execution environments are properly configured
    (e.g. OpenFOAM installation, SSH access, scheduler availability)

Authors
  Simon A. Rodriguez, University College Dublin (UCD)
  Alojz Ivankovic, University College Dublin (UCD)
  Petar Cosic, University College Dublin (UCD)
  Tom Flint, University of Manchester (UoM)
  Philip Cardiff, University College Dublin (UCD)
"""


from __future__ import annotations
from pathlib import Path
from typing import Optional


def run_generate(config_path: str, workdir: Optional[str] = None) -> None:
    """
    Entry point for `simtopc generate`.

    - Does NOT assume a repository layout.
    - Uses the directory containing config.yml as the default working directory,
      so relative files like parameters.txt resolve as expected.
    """
    from simtopc.config import load_config
    from simtopc.generate import legacy_funcs as lf

    cfg_path = Path(config_path).expanduser().resolve()
    if not cfg_path.exists():
        raise FileNotFoundError(cfg_path)

    cfg_all = load_config(str(cfg_path))
    if cfg_all is None:
        raise RuntimeError(f"Failed to load config: {cfg_path}")

    # Working directory (default: folder containing config.yml)
    wd = Path(workdir).expanduser().resolve() if workdir else cfg_path.parent
    if not wd.exists():
        raise FileNotFoundError(wd)

    import os
    old_cwd = Path.cwd()
    os.chdir(str(wd))
    try:
        print("Beginning data generation")
        running_on = cfg_all.running_on
        mesh_density = cfg_all.mesh_density
        mesh_density_raw = cfg_all.mesh_density
        mesh_label = Path(str(mesh_density_raw)).name 
        openfoam_version = getattr(cfg_all, "openfoam_version", "2412")
        status_check_frequency_min = int(getattr(cfg_all, "status_check_frquency_in_min", "2"))
        hostname, run_address, of_location = lf.set_environment_variables(running_on)
        base_case_name = lf.set_base_case_name(mesh_density, openfoam_version)

        # Keep legacy behavior: parameters.txt relative to working dir
        params_file = Path(getattr(cfg_all, "parameters_file", "parameters.txt"))
        if not params_file.exists():
            raise FileNotFoundError(
                f"Could not find parameters file: {params_file.resolve()}\n"
                f"Working directory is: {Path.cwd()}\n"
                f"Hint: place parameters.txt next to config.yml or set `parameters_file:` in the config."
            )

        import numpy as np
        parameters = np.loadtxt(str(params_file), skiprows=1)
        number_cases = parameters.shape[0]

        lf.create_simulation_cases(number_cases, base_case_name, parameters, mesh_density, openfoam_version)

        if running_on == "LOCAL":
            for i in range(number_cases):
                name_new_folder = f"{mesh_label}/test_case_{i + 1}"
                lf.terminal(f"cd {name_new_folder}/system/ && mv decomposeParDict_16cores decomposeParDict")
                lf.terminal(f'bash -c "source {of_location} && cd {name_new_folder} && ./Allrun_local"')
        else:
            for i in range(number_cases):
                name_new_folder = f"{mesh_label}/test_case_{i + 1}"
                lf.terminal(f'bash -c "source {of_location} && cd {name_new_folder} && cp -r initial 0"')
                lf.terminal(f'bash -c "source {of_location} && cd {name_new_folder} && blockMesh"')
                lf.terminal(f'bash -c "source {of_location} && cd {name_new_folder} && setSolidFraction"')
                lf.terminal(f'bash -c "source {of_location} && cd {name_new_folder} && decomposePar"')

                print("Transferring the test case ", str(i + 1))

                if i == 0:
                    lf.terminal(f'ssh {hostname} "cd {run_address} && mkdir {mesh_label}"')

                print("scp -r " + name_new_folder +" " + hostname+ ":" + run_address + name_new_folder, "\n")
                lf.terminal("scp -r " + name_new_folder +" " + hostname+ ":" + run_address + name_new_folder)

                job_id = lf.submit_remote_job(hostname, f"{run_address}{name_new_folder}", name_new_folder, running_on)
                lf.monitor_job_is_running(job_id, hostname, status_check_frequency_min)

                lf.terminal(
                    'ssh {host} "cd {run}{folder} && cd .. && '
                    'zip -r test_case_{idx}.zip test_case_{idx} && '
                    '[ -f test_case_{idx}.zip ] && rm -r test_case_{idx} && '
                    'echo \\"Compression successful and folder deleted.\\""'.format(
                        host=hostname, run=run_address, folder=name_new_folder, idx=str(i + 1)
                    )
                )

                lf.terminal(f"scp -r {hostname}:{run_address}{name_new_folder}.zip ./{mesh_label}/")
                lf.terminal(f'ssh {hostname} "cd {run_address}{mesh_label} && rm *.zip "')
                lf.terminal(f"rm -r {name_new_folder}")

        # Unzip results
        for i in range(number_cases):
            name_new_folder = f"{mesh_label}/test_case_{i + 1}"
            lf.terminal(f"unzip {name_new_folder}.zip -d {mesh_label}/")
            lf.terminal(f"rm {name_new_folder}.zip")

        print("Data generation completed.")

    finally:
        os.chdir(str(old_cwd))