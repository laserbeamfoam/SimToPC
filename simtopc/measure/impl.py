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
                                          _measure_results_dir,
                                          plotResults,
                                          )
from simtopc.measure.cells import read_cell_grid
from simtopc.measure.metallographic import (laser_off_time_from_case, lateral_cells,
                                            measure_sections, sections_in_window,
                                            steady_sections)
from joblib import dump

CROSS_SECTION_COLUMNS = ["iy", "width", "height", "depth", "porosity_at_iy",
                         "total_volume_material_at_iy"]


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

def measurement_window(measure_cfg, spot_size):
    """Track window [begin, end] of the measured sections: [y_begin, y_end] less the trim."""
    trim = measure_cfg.trim
    begin = float(measure_cfg.y_begin)
    end = float(measure_cfg.y_end)
    if trim.enabled:
        begin += trim.start_spot_sizes * spot_size
        end -= trim.end_spot_sizes * spot_size
    if end <= begin:
        raise ValueError("Requested trimming removes the full requested track window.")
    return begin, end


def read_case_grid(name_new_folder, measure_cfg, need_solidification_time=False):
    return read_cell_grid(
        Path(name_new_folder),
        axes=measure_cfg.axes,
        melt_field=measure_cfg.melt_field,
        metal_field=measure_cfg.metal_field,
        cell_size=measure_cfg.cell_size,
        need_solidification_time=need_solidification_time,
    )


def _sections_of_statistics(name_new_folder, stats, grid):
    """Track indices of the sections of a single-track cross_sections_statistics table
    (iy is the lower face of a layer of cells)."""
    position = (stats["iy"].to_numpy() - grid.origin[0]) / grid.cell_size
    sections = np.rint(position).astype(int)
    if sections.size and ((np.abs(position - sections) > 1e-3).any() or sections.min() < 0
                          or sections.max() >= grid.shape[0]):
        raise ValueError(
            f"The measured sections of {name_new_folder} are not on the cell faces "
            "of the mesh along the track.")
    return sections


def select_steady_sections(name_new_folder, measure_cfg, grid, candidates, lateral=None):
    """Steady sections among the candidates (see metallographic.steady_sections); writes
    steady_sections.csv and returns the steady section indices."""
    t_off = measure_cfg.laser_off_time
    if t_off is None:
        t_off = laser_off_time_from_case(name_new_folder)
    ks, p90 = steady_sections(grid, candidates, measure_cfg.substrate_top, t_off, lateral)
    pd.DataFrame({
        "section": candidates,
        "track_coordinate": grid.centres(0)[candidates],
        "p90_solidification_time": p90,
        "steady": np.isin(candidates, ks),
    }).to_csv(_measure_results_dir(name_new_folder) / "steady_sections.csv", index=False,
              encoding="utf-8")
    if ks.size == 0:
        raise ValueError(
            f"No steady section in the measured window of {name_new_folder}: no section "
            f"solidified in the substrate before the laser was switched off ({t_off} s).")
    print(f"Steady sections: {ks.size} of {len(candidates)}, track "
          f"{grid.centres(0)[ks[0]]:.6g} to {grid.centres(0)[ks[-1]]:.6g} m")
    return ks


def steady_single_track(name_new_folder, measure_cfg, grid):
    """Keep the steady sections of the single-track statistics (all the sections are kept
    in cross_sections_statistics_all_sections.csv)."""
    results_dir = _measure_results_dir(name_new_folder)
    csv_path = results_dir / "cross_sections_statistics.csv"
    if not csv_path.exists():
        print("No cross-section statistics (melt pool not continuous): no steady sections.")
        return None
    stats = pd.read_csv(csv_path)
    sections = _sections_of_statistics(name_new_folder, stats, grid)
    ks = select_steady_sections(name_new_folder, measure_cfg, grid, sections)
    stats.to_csv(results_dir / "cross_sections_statistics_all_sections.csv", index=False,
                 encoding="utf-8")
    stats[np.isin(sections, ks)].to_csv(csv_path, index=False, encoding="utf-8")
    plotResults(name_new_folder, CSV_CROSS_SECTIONS=str(csv_path))
    return ks


def measure_case_metallographic(name_new_folder, measure_cfg, spot_size, grid=None):
    """Metallographic cross-sections of one case (see simtopc.measure.metallographic):
    writes cross_sections_statistics.csv (the columns of the single-track mode),
    metallographic_sections.csv and the continuity flags; returns the statistics."""
    grid = grid if grid is not None else read_case_grid(
        name_new_folder, measure_cfg, need_solidification_time=measure_cfg.steady_sections)
    begin, end = measurement_window(measure_cfg, spot_size)
    sections = sections_in_window(grid, begin, end)
    if sections.size == 0:
        raise ValueError(
            f"No cross-section of {name_new_folder} has its cell centre in the "
            f"measurement window [{begin}, {end}] along {grid.axes.track}."
        )
    lateral = lateral_cells(grid, measure_cfg.x_min, measure_cfg.x_max)
    if measure_cfg.steady_sections:
        sections = select_steady_sections(name_new_folder, measure_cfg, grid, sections, lateral)
    results = measure_sections(grid, sections, measure_cfg.substrate_top, lateral)
    h3 = grid.cell_size ** 3
    rows = []
    for r in results:
        total = r.void_cells + r.solid_cells
        rows.append([r.track, r.width, r.height, r.depth,
                     r.void_cells / total if total else 0.0, total * h3])
    stats = pd.DataFrame(rows, columns=CROSS_SECTION_COLUMNS)

    continuous = all(r.fused for r in results)
    aux_dir = _measure_aux_dir(name_new_folder)
    dump(continuous, str(aux_dir / "continuous.joblib"))
    if not continuous:
        dump([r.track for r in results if not r.fused], str(aux_dir / "void_iy_levels.joblib"))
        print(f"Warning: the track of {name_new_folder} is not fused into the substrate "
              "in every section (not continuous).")
    results_dir = _measure_results_dir(name_new_folder)
    stats.to_csv(results_dir / "cross_sections_statistics.csv", index=False, encoding="utf-8")
    pd.DataFrame({
        "section": sections,
        "track_coordinate": [r.track for r in results],
        "width": [r.width for r in results],
        "depth": [r.depth for r in results],
        "height": [r.height for r in results],
        "fused": [r.fused for r in results],
        "void_cells": [r.void_cells for r in results],
        "consolidated_cells": [r.solid_cells for r in results],
    }).to_csv(results_dir / "metallographic_sections.csv", index=False, encoding="utf-8")
    print("Generating profiles for the variables")
    plotResults(name_new_folder,
                CSV_CROSS_SECTIONS=str(results_dir / "cross_sections_statistics.csv"))
    return stats


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

        laser_radius_i = parameters[i, 2] / 2
        if measure_cfg.geometry_mode == "metallographic":
            print(f"\n Measuring the metallographic cross-sections of test_case_{i+1}")
            measure_case_metallographic(name_new_folder, measure_cfg,
                                        spot_size=2 * laser_radius_i)
            print(f"\nFinished measuring geometry-based quantities "
                  f"for test_case_{i + 1}\n")
            continue

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
        if measure_cfg.steady_sections:
            grid = read_case_grid(name_new_folder, measure_cfg,
                                  need_solidification_time=True)
            steady_single_track(name_new_folder, measure_cfg, grid)

        print(f"\nFinished measuring geometry-based quantities "
              f"for test_case_{i + 1}\n")

    print("Geometry measurement finished.")
