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
        # print("mesh_density is", mesh_density, "\n")
        mesh_density_raw = cfg_all.mesh_density
        # print("mesh_density_raw is", mesh_density_raw, "\n")
        mesh_label = Path(str(mesh_density_raw)).name  # => "COARSE" aunque venga un path largo
        # print("mesh_label is", mesh_label, "\n")
        openfoam_version = getattr(cfg_all, "openfoam_version", "2412")
        status_check_frequency_min = int(getattr(cfg_all, "status_check_frquency_in_min", "2"))

        hostname, run_address, of_location = lf.set_environment_variables(running_on)
        print(f"[generate] running_on={running_on}")
        print(f"[generate] hostname={hostname}")
        print(f"[generate] run_address={run_address!r}")

        print("\n \n \n \n \n")
        # exit()


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
                # name_new_folder = f"{mesh_density}/test_case_{i + 1}"
                name_new_folder = f"{mesh_label}/test_case_{i + 1}"
                lf.terminal(f"cd {name_new_folder}/system/ && mv decomposeParDict_16cores decomposeParDict")
                lf.terminal(f'bash -c "source {of_location} && cd {name_new_folder} && ./Allrun_local"')
        else:
            for i in range(number_cases):
                # name_new_folder = f"{mesh_density}/test_case_{i + 1}"
                name_new_folder = f"{mesh_label}/test_case_{i + 1}"

                lf.terminal(f'bash -c "source {of_location} && cd {name_new_folder} && cp -r initial 0"')
                lf.terminal(f'bash -c "source {of_location} && cd {name_new_folder} && blockMesh"')
                lf.terminal(f'bash -c "source {of_location} && cd {name_new_folder} && setSolidFraction"')
                lf.terminal(f'bash -c "source {of_location} && cd {name_new_folder} && decomposePar"')

                print("Transferring the test case ", str(i + 1))

                # print(f"[generate] running_on={running_on}")
                # print(f"[generate] hostname={hostname}")
                # print(f"[generate] run_address={run_address!r}")

                if i == 0:
                    print("HERE")
                    # cmd = f'ssh {hostname} "cd {run_address} && mkdir {mesh_density}"'
                    # cmd = f'ssh {hostname} "cd {run_address} && mkdir {mesh_density}"'
                    # print("CMD =", cmd, "\n")
                    # lf.terminal(cmd)
                    # print("HERE2")
                    # lf.terminal(f'ssh {hostname} "cd {run_address} && mkdir {mesh_density}"')
                    lf.terminal(f'ssh {hostname} "cd {run_address} && mkdir {mesh_label}"')
                    print("HERE3", "\n")


                # lf.terminal(f"scp -r {name_new_folder} {hostname}:{run_address}{name_new_folder}")
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

                # lf.terminal(f"scp -r {hostname}:{run_address}{name_new_folder}.zip ./{mesh_density}/")
                lf.terminal(f"scp -r {hostname}:{run_address}{name_new_folder}.zip ./{mesh_label}/")
                # lf.terminal(f'ssh {hostname} "cd {run_address}{mesh_density} && rm *.zip "')
                lf.terminal(f'ssh {hostname} "cd {run_address}{mesh_label} && rm *.zip "')
                lf.terminal(f"rm -r {name_new_folder}")

        # Unzip results
        for i in range(number_cases):
            # name_new_folder = f"{mesh_density}/test_case_{i + 1}"
            name_new_folder = f"{mesh_label}/test_case_{i + 1}"
            # lf.terminal(f"unzip {name_new_folder}.zip -d {mesh_density}/")
            lf.terminal(f"unzip {name_new_folder}.zip -d {mesh_label}/")
            lf.terminal(f"rm {name_new_folder}.zip")

        print("Data generation completed.")

    finally:
        os.chdir(str(old_cwd))
