from __future__ import annotations

from pathlib import Path
import numpy as np

from pathlib import Path
import shutil
# from importlib import resources
# resources: use stdlib on Python>=3.9; otherwise use backport on 3.8
from importlib import resources as _stdlib_resources

if hasattr(_stdlib_resources, "files") and hasattr(_stdlib_resources, "as_file"):
    resources = _stdlib_resources
else:
    import importlib_resources as resources  # type: ignore

import json


def copy_measure_resources(case_dir: Path) -> None:
    """
    Copy helper scripts into a case directory from packaged resources.
    This avoids relying on a repo-local 'src/' folder and works after pip install.
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


# IMPORTANTE: aquí todavía usas esas funciones, pero YA NO desde "src".
# En el siguiente paso las moveremos dentro del paquete.
from simtopc.measure.legacy_funcs import (  # lo crearemos en el paso 4
    set_environment_variables,
    terminal,
    calculate_geometry_full_meltpool,
)

def run_measure_cases(cfg_all, measure_cfg, config_path: Path) -> None:
    # source the correct OpenFOAM, based on the system and OF version
    hostname, run_address, OF_LOCATION = set_environment_variables(cfg_all.running_on)

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


       
        (case_dir / "measure_inputs.json").write_text(json.dumps(payload, indent=2))


        print(f"\n Measuring geometry-based quantities for test_case_{i+1}")

        # NOTA: estos "cp src/..." los vamos a cambiar pronto por "copiar desde package"
        # pero por hoy, vamos a mantenerlo igual para no romper el workflow.
        # terminal(f'cp src/extract* {name_new_folder}/')
        # terminal(f'cp src/quantities_from_meltpool.py {name_new_folder}/')
        # terminal(f'cp src/functions.py {name_new_folder}/')
        copy_measure_resources(Path(name_new_folder))

        # print("HERE")
        # exit()

        laser_radius_i = parameters[i, 2] / 2
        # terminal(f'cd {name_new_folder} && mv *png images_full_meltpool/')
        # terminal(f'cd {name_new_folder} && rm *.py')
        # terminal(f'cd {name_new_folder} && rm -f *.py')

        # print(OF_LOCATION)
        terminal(f'bash -lc "source {OF_LOCATION} && cd {name_new_folder} && pvpython extract_meltpool.py"')
        # terminal(f'bash -c "source {OF_LOCATION} && cd {name_new_folder} && pvpython extract_meltpool.py"')

        calculate_geometry_full_meltpool(
            name_new_folder,
            laser_radius_i,
            measure_cfg,
            CSV_3D=name_new_folder + "/meltpool.csv"
        )

        terminal(f'cd {name_new_folder} && mkdir images_full_meltpool')
        terminal(f'cd {name_new_folder} && mv *png images_full_meltpool/')

        print(f"\n Finished measuring geometry-based quantities for test_case_{i+1}\n")

    print("Geometry measurement finished.")
