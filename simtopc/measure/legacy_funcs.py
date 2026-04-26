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
  Legacy helper functions implementing geometry-based measurements of
  melt-pool cross-sections in SimToPC.

  This module contains low-level routines used to analyse discretised
  melt-pool geometry extracted from simulation data. The implemented
  algorithms compute continuity, cross-sectional dimensions, porosity
  metrics, and derived geometric quantities based on structured field
  data.

  The functions in this module are primarily intended for internal use
  by the SimToPC measurement workflow.

Assumptions
  - Input geometry is provided as discretised point data on a uniform grid
  - Measurement parameters are supplied via a validated MeasureConfig object
  - Melt-pool geometry corresponds to a single-track configuration
  - Numerical tolerances are handled via explicit rounding operations

Authors
  Simon A. Rodriguez, University College Dublin (UCD)
  Alojz Ivankovic, University College Dublin (UCD)
  Petar Cosic, University College Dublin (UCD)
  Tom Flint, University of Manchester (UoM)
  Philip Cardiff, University College Dublin (UCD)
"""

import os
import re
from dataclasses import dataclass
from joblib import dump, load
import numpy as np
import pandas as pd
import random
import subprocess
import time
import importlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from pathlib import Path


ROUND_DECIMALS = 8
ROUND_TOL = 10 ** (-ROUND_DECIMALS)
MEASURE_RESULTS_DIRNAME = "measure_results"
MEASURE_AUX_DIRNAME = "measure_aux"
MEASURE_WORK_DIRNAME = "measure_work"


@dataclass(frozen=True)
class AnalysisWindow:
    y_values: np.ndarray
    y_data_min: float
    y_data_max: float
    x_mid_section_snapped: float
    y_merge_tol: float
    y_effective_begin: float
    y_effective_end: float
    trim_start: float
    trim_end: float
    y_trimmed_begin_physical: float
    y_trimmed_end_physical: float
    y_levels: np.ndarray
    y_levels_actual: np.ndarray
    nominal_mismatch: bool
    trim_snapped: bool


@dataclass(frozen=True)
class SectionSupport:
    y_reported: float
    y_actual: float
    z_values: np.ndarray
    supported_z_levels: int

    @property
    def is_valid(self) -> bool:
        return self.supported_z_levels > 0


@dataclass(frozen=True)
class SectionGeometry:
    cells: pd.DataFrame
    x_values: np.ndarray
    y_values: np.ndarray
    z_values: np.ndarray
    x_min_mesh: float
    x_max_mesh: float
    z_min_mesh: float
    z_max_mesh: float


@dataclass(frozen=True)
class RowEvaluation:
    x_min_mesh: float
    x_max_mesh: float
    row_has_pores: bool
    n_pores: int
    width_row: float
    number_non_void_cells: int
    pore_locations: list
    pores_are_internal: list


def terminal(command):
    os.system(command)

# def set_environment_variables(running_on: str):
#     variables_import = "simtopc.input_files." + running_on.lower() + "_inp"
#     imported = importlib.import_module(variables_import)
#     hostname = imported.hostname
#     run_address = imported.run_address
#     OF_LOCATION = imported.OF_LOCATION
#     return hostname, run_address, OF_LOCATION
def set_environment_variables(env):
    hostname = env.hostname
    run_address = env.run_address
    OF_LOCATION = env.of_location
    return hostname, run_address, OF_LOCATION


def _round_scalar(value):
    return float(np.round(float(value), ROUND_DECIMALS))


def _round_array(values):
    return np.round(np.asarray(values, dtype=float), ROUND_DECIMALS)


def _round_to_mesh(value, cell_size):
    return _round_scalar(np.round(float(value) / cell_size) * cell_size)


def _round_array_to_mesh(values, cell_size):
    return _round_array(np.round(np.asarray(values, dtype=float) / cell_size) * cell_size)


def _deduplicate_levels(levels, merge_tol):
    if levels.size == 0:
        return levels
    deduped = [levels[0]]
    for level in levels[1:]:
        if abs(level - deduped[-1]) > merge_tol:
            deduped.append(level)
    return np.asarray(deduped, dtype=float)


def _count_supported_z_levels(z_values, cell_size):
    z_values = _round_array(z_values)
    if z_values.size == 0:
        return 0
    z_min = _round_to_mesh(np.min(z_values), cell_size)
    z_max = _round_to_mesh(np.max(z_values), cell_size)
    z_level = z_min
    levels_count = 0
    while z_level <= z_max:
        if np.sum(np.isclose(z_values, z_level)) >= 1:
            levels_count += 1
        z_level = _round_scalar(z_level + cell_size)
    return levels_count


def _evaluate_section_support(y_reported, y_actual, y_values, z_values, y_tol, cell_size):
    if np.isnan(y_actual):
        return SectionSupport(
            y_reported=float(y_reported),
            y_actual=float("nan"),
            z_values=np.asarray([], dtype=float),
            supported_z_levels=0,
        )

    section_z_values = _round_array(z_values[np.isclose(y_values, y_actual, atol=y_tol)])
    return SectionSupport(
        y_reported=float(y_reported),
        y_actual=float(y_actual),
        z_values=section_z_values,
        supported_z_levels=_count_supported_z_levels(section_z_values, cell_size),
    )


def _build_section_geometry(df, y_actual, y_values, y_tol, cell_size):
    section_mask = np.isclose(y_values, y_actual, atol=y_tol)
    cells_at_section = df[section_mask]
    x_at_section = _round_array(cells_at_section["Points_0"].to_numpy())
    y_at_section = _round_array(cells_at_section["Points_1"].to_numpy())
    z_at_section = _round_array(cells_at_section["Points_2"].to_numpy())

    x_min_mesh = _round_to_mesh(np.min(x_at_section), cell_size)
    x_max_mesh = _round_to_mesh(np.max(x_at_section), cell_size)
    z_min_mesh = _round_to_mesh(np.min(z_at_section), cell_size)
    z_max_mesh = _round_to_mesh(np.max(z_at_section), cell_size)

    return SectionGeometry(
        cells=cells_at_section,
        x_values=x_at_section,
        y_values=y_at_section,
        z_values=z_at_section,
        x_min_mesh=x_min_mesh,
        x_max_mesh=x_max_mesh,
        z_min_mesh=z_min_mesh,
        z_max_mesh=z_max_mesh,
    )


def _evaluate_section_row(cells_at_iy, x_at_iy, z_at_iy, iz, cell_size):
    mask_at_row = (iz == _round_array(z_at_iy))
    cells_at_iy_iz = cells_at_iy[mask_at_row]
    x_at_iy_iz = cells_at_iy_iz["Points_0"].to_numpy()
    if x_at_iy_iz.shape[0] == 0:
        return None

    min_x_at_iy_iz_that_is_in_original_mesh = _round_to_mesh(
        np.min(x_at_iy_iz),
        cell_size,
    )
    max_x_at_iy_iz_that_is_in_original_mesh = _round_to_mesh(
        np.max(x_at_iy_iz),
        cell_size,
    )

    distance_minx_max_at_zlevel = _round_scalar(
        max_x_at_iy_iz_that_is_in_original_mesh
        - min_x_at_iy_iz_that_is_in_original_mesh
    )
    expected_number_cells_at_iy_iz = int(distance_minx_max_at_zlevel / cell_size)

    ix = min_x_at_iy_iz_that_is_in_original_mesh
    number_non_void_cells_in_row = 0
    row_has_pores = False
    n_pores_in_row = 0
    width_row = _round_scalar(
        max_x_at_iy_iz_that_is_in_original_mesh
        - min_x_at_iy_iz_that_is_in_original_mesh
    )

    pore_locations_at_row_i = []
    pores_at_row_i_are_internal = []
    if expected_number_cells_at_iy_iz > 1:
        x_at_iy_iz_rounded = _round_array(x_at_iy_iz)
        while ix < max_x_at_iy_iz_that_is_in_original_mesh:
            if np.sum(np.isclose(ix, x_at_iy_iz_rounded)) > 0:
                number_non_void_cells_in_row += 1
            else:
                n_pores_in_row += 1
                row_has_pores = True
                pore_locations_at_row_i.append(ix)
                mask_at_ix = np.isclose(ix, x_at_iy)
                cells_at_ix_iy = cells_at_iy[mask_at_ix]
                z_at_ix_iy = cells_at_ix_iy["Points_2"]
                pores_at_row_i_are_internal.append(np.sum(iz < z_at_ix_iy) > 0)
            ix = _round_scalar(ix + cell_size)

    if expected_number_cells_at_iy_iz == 1:
        number_non_void_cells_in_row = 1

    return RowEvaluation(
        x_min_mesh=min_x_at_iy_iz_that_is_in_original_mesh,
        x_max_mesh=max_x_at_iy_iz_that_is_in_original_mesh,
        row_has_pores=row_has_pores,
        n_pores=n_pores_in_row,
        width_row=width_row,
        number_non_void_cells=number_non_void_cells_in_row,
        pore_locations=pore_locations_at_row_i,
        pores_are_internal=pores_at_row_i_are_internal,
    )


def _snap_value_to_global_mesh(value, cell_size, direction):
    scaled = value / cell_size
    if direction == "forward":
        snapped = np.ceil(scaled - ROUND_TOL)
    elif direction == "backward":
        snapped = np.floor(scaled + ROUND_TOL)
    else:
        raise ValueError(f"Unknown snapping direction: {direction}")
    return _round_scalar(snapped * cell_size)


def _compute_analysis_y_levels(df, measure_cfg, spot_size):
    y_begin = float(measure_cfg.y_begin)
    y_end = float(measure_cfg.y_end)
    cell_size = float(measure_cfg.cell_size)

    if y_end <= y_begin:
        raise ValueError(
            f"Invalid measurement window: y_end ({y_end}) must be greater "
            f"than y_begin ({y_begin})."
        )
    if cell_size <= 0:
        raise ValueError(
            f"Invalid cell size: cell_size must be positive, got {cell_size}."
        )

    x_values = _round_array(df["Points_0"].to_numpy())
    y_values = _round_array(df["Points_1"].to_numpy())
    if y_values.size == 0 or x_values.size == 0:
        raise ValueError("The meltpool dataset is empty; no x/y levels were found.")

    x_mid_section = _round_scalar((measure_cfg.x_min + measure_cfg.x_max) / 2)
    unique_x = np.unique(x_values)
    x_mid_section_snapped = unique_x[np.argmin(np.abs(unique_x - x_mid_section))]
    canonical_slice_mask = np.isclose(x_values, x_mid_section_snapped)
    canonical_y_raw = y_values[canonical_slice_mask]
    canonical_z_raw = _round_array(df.loc[canonical_slice_mask, "Points_2"].to_numpy())
    canonical_y_levels = np.sort(np.unique(canonical_y_raw))
    merge_tol = max(ROUND_TOL, 0.25 * cell_size)
    canonical_y_levels = _deduplicate_levels(
        canonical_y_levels,
        merge_tol=merge_tol,
    )
    supported_levels = []
    for level in canonical_y_levels:
        z_values_at_level = canonical_z_raw[np.isclose(canonical_y_raw, level, atol=merge_tol)]
        if _count_supported_z_levels(z_values_at_level, cell_size) >= measure_cfg.min_points_per_zrow:
            supported_levels.append(level)
    canonical_y_levels = np.asarray(supported_levels, dtype=float)

    if canonical_y_levels.size == 0:
        raise ValueError(
            "No y-levels were found on the canonical meltpool slice used for "
            "continuity analysis."
        )

    y_data_min = float(np.min(canonical_y_levels))
    y_data_max = float(np.max(canonical_y_levels))
    y_effective_begin = max(y_begin, y_data_min)
    y_effective_end = min(y_end, y_data_max)

    if y_effective_end <= y_effective_begin:
        raise ValueError(
            "The requested measurement window does not overlap with the "
            "observed meltpool window."
        )

    trim_cfg = measure_cfg.trim
    trim_start_spot_sizes = trim_cfg.start_spot_sizes if trim_cfg.enabled else 0.0
    trim_end_spot_sizes = trim_cfg.end_spot_sizes if trim_cfg.enabled else 0.0

    if trim_start_spot_sizes < 0 or trim_end_spot_sizes < 0:
        raise ValueError("Trimming values must be non-negative.")

    trim_start = trim_start_spot_sizes * spot_size
    trim_end = trim_end_spot_sizes * spot_size
    requested_length = y_end - y_begin

    if trim_start + trim_end >= requested_length:
        raise ValueError(
            "Requested trimming removes the full requested track window."
        )

    y_trimmed_begin_physical = y_begin + trim_start
    y_trimmed_end_physical = y_end - trim_end
    y_measurable_begin_physical = max(y_trimmed_begin_physical, y_data_min)
    y_measurable_end_physical = min(y_trimmed_end_physical, y_data_max)

    if y_measurable_end_physical <= y_measurable_begin_physical:
        raise ValueError(
            "The trimmed measurement window does not overlap with the "
            "observed meltpool window."
        )

    mesh_begin = _snap_value_to_global_mesh(
        y_measurable_begin_physical,
        cell_size,
        direction="forward",
    )
    mesh_end = _snap_value_to_global_mesh(
        y_measurable_end_physical,
        cell_size,
        direction="backward",
    )

    if mesh_end < mesh_begin:
        raise ValueError(
            "No measurable y-sections remain after trimming and mesh snapping."
        )

    n_levels = int(np.floor(((mesh_end - mesh_begin) / cell_size) + ROUND_TOL)) + 1
    y_levels_report = _round_array(
        mesh_begin + np.arange(n_levels, dtype=float) * cell_size
    )
    actual_y_levels = []
    for y_level in y_levels_report:
        idx = int(np.argmin(np.abs(canonical_y_levels - y_level)))
        nearest = canonical_y_levels[idx]
        if abs(nearest - y_level) <= merge_tol:
            actual_y_levels.append(nearest)
        else:
            actual_y_levels.append(np.nan)

    actual_y_levels = np.asarray(actual_y_levels, dtype=float)
    if y_levels_report.size == 0:
        raise ValueError("No measurable y-sections remain after trimming.")

    nominal_mismatch = (
        abs(y_effective_begin - y_begin) > ROUND_TOL
        or abs(y_effective_end - y_end) > ROUND_TOL
    )
    trim_snapped = (
        abs(mesh_begin - y_measurable_begin_physical) > ROUND_TOL
        or abs(mesh_end - y_measurable_end_physical) > ROUND_TOL
    )

    return AnalysisWindow(
        y_values=y_values,
        y_data_min=y_data_min,
        y_data_max=y_data_max,
        x_mid_section_snapped=_round_scalar(x_mid_section_snapped),
        y_merge_tol=merge_tol,
        y_effective_begin=_round_scalar(y_effective_begin),
        y_effective_end=_round_scalar(y_effective_end),
        trim_start=trim_start,
        trim_end=trim_end,
        y_trimmed_begin_physical=_round_scalar(y_trimmed_begin_physical),
        y_trimmed_end_physical=_round_scalar(y_trimmed_end_physical),
        y_levels=y_levels_report,
        y_levels_actual=actual_y_levels,
        nominal_mismatch=nominal_mismatch,
        trim_snapped=trim_snapped,
    )


def _emit_analysis_window_warnings(name_new_folder, measure_cfg, analysis_window):
    if analysis_window.nominal_mismatch:
        print(
            "Warning: requested measurement window "
            f"[{measure_cfg.y_begin}, {measure_cfg.y_end}] was reduced to "
            "the observed meltpool window "
            f"[{analysis_window.y_effective_begin}, {analysis_window.y_effective_end}] "
            f"for {name_new_folder}."
        )
    if analysis_window.trim_snapped:
        print(
            "Warning: trimming boundaries were snapped to the mesh for "
            f"{name_new_folder}. Physical trimmed window "
            f"[{analysis_window.y_trimmed_begin_physical}, "
            f"{analysis_window.y_trimmed_end_physical}] became reported window "
            f"[{analysis_window.y_levels[0]}, {analysis_window.y_levels[-1]}]."
        )


def _measure_results_dir(name_new_folder):
    results_dir = Path(name_new_folder) / MEASURE_RESULTS_DIRNAME
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


def _measure_aux_dir(name_new_folder):
    aux_dir = Path(name_new_folder) / MEASURE_AUX_DIRNAME
    aux_dir.mkdir(parents=True, exist_ok=True)
    return aux_dir


def _measure_work_dir(name_new_folder):
    work_dir = Path(name_new_folder) / MEASURE_WORK_DIRNAME
    work_dir.mkdir(parents=True, exist_ok=True)
    return work_dir



def is_meltpool_continuous(name_new_folder, laser_radius_test_case_i, 
                            measure_cfg, CSV_3D="meltpool.csv"):

    cell_size = measure_cfg.cell_size


    df = pd.read_csv(CSV_3D)
    analysis_window = _compute_analysis_y_levels(
        df,
        measure_cfg,
        spot_size=2 * laser_radius_test_case_i,
    )
    x = _round_array(df["Points_0"].to_numpy())
    y = analysis_window.y_values
    z = _round_array(df["Points_2"].to_numpy())
    meltpool_is_continuous = True
    y_levels = analysis_window.y_levels
    y_levels_actual = analysis_window.y_levels_actual
    y_merge_tol = analysis_window.y_merge_tol
    # First, check if a y-z slice at the canonical x location is continuous.
    x_mid_section_snapped = analysis_window.x_mid_section_snapped
    mask_x_mid_section = np.isclose(x, x_mid_section_snapped)
    mid_plane_x = df[mask_x_mid_section]
    y_at_mid_plane_x = _round_array(mid_plane_x["Points_1"].to_numpy())
    z_at_mid_plane_x = _round_array(mid_plane_x["Points_2"].to_numpy())

    # This loop answers the question: are there cells with less than 3 cells
    # (or 4 points) aligned along the z-axis for every y-location in the 
    # x_mid_plane?
    for y_level, y_level_actual in zip(y_levels, y_levels_actual):
        section_support = _evaluate_section_support(
            y_reported=y_level,
            y_actual=y_level_actual,
            y_values=y_at_mid_plane_x,
            z_values=z_at_mid_plane_x,
            y_tol=y_merge_tol,
            cell_size=cell_size,
        )
        z_at_y_level_and_x_mid_plane = section_support.z_values
        if not section_support.is_valid:
            meltpool_is_continuous = False
            break
        z_min_at_y_level_and_x_mid_plane = np.min(z_at_y_level_and_x_mid_plane)
        z_max_at_y_level_and_x_mid_plane = np.max(z_at_y_level_and_x_mid_plane)
        z_min_at_iy_that_is_in_original_mesh = _round_to_mesh(
            z_min_at_y_level_and_x_mid_plane,
            cell_size,
        )
        z_max_at_iy_that_is_in_original_mesh = _round_to_mesh(
            z_max_at_y_level_and_x_mid_plane,
            cell_size,
        )
        z0_at_y_level = z_min_at_iy_that_is_in_original_mesh
        expected_levels_count = np.round((z_max_at_iy_that_is_in_original_mesh 
                           - z_min_at_iy_that_is_in_original_mesh) / cell_size)
        levels_count = 0
        while (z0_at_y_level <= z_max_at_iy_that_is_in_original_mesh):
            mask = (np.round(z0_at_y_level, 8) == np.round(
                                              z_at_y_level_and_x_mid_plane, 8))    
            if (np.sum(mask) >= 1):
                levels_count = levels_count + 1
            z0_at_y_level = _round_scalar(z0_at_y_level + cell_size)
        if levels_count < measure_cfg.min_points_per_zrow:
            meltpool_is_continuous = False
            break
    aux_dir = _measure_aux_dir(name_new_folder)
    dump(meltpool_is_continuous, str(aux_dir / "continuous.joblib"))
                
    if (not meltpool_is_continuous): 
        void_iy_levels = []
        for iy, iy_actual in zip(y_levels, y_levels_actual):
            section_support = _evaluate_section_support(
                y_reported=iy,
                y_actual=iy_actual,
                y_values=y,
                z_values=z,
                y_tol=y_merge_tol,
                cell_size=cell_size,
            )
            if not section_support.is_valid:
                void_iy_levels.append(iy)
        if (len(void_iy_levels) > 0):
            dump(void_iy_levels, str(aux_dir / "void_iy_levels.joblib"))
    return meltpool_is_continuous


def calculate_cross_sections_statistics(name_new_folder, row_statistics, 
                                        pore_locatios_at_rows, 
                                        pores_at_row_are_internal, 
                                        meltpool_is_continuous,
                                        measure_cfg):
    cell_size = measure_cfg.cell_size

    cross_sections_statistics = []
    y = row_statistics["y_coord"].to_numpy()
    row_has_pores = row_statistics["row_has_pores"]
    y_unique = np.unique(y)  
    void_iy_levels= []
    if (not meltpool_is_continuous):
        void_iy_levels = load(str(_measure_aux_dir(name_new_folder) / "void_iy_levels.joblib"))
    
    for iy in y_unique:
        if not np.any(np.isclose(iy, void_iy_levels)):
            mask = (iy == y)
            cross_section_at_iy = row_statistics[mask]
            z_at_iy = cross_section_at_iy["z_coord_"]
            pores_at_iy = cross_section_at_iy["row_has_pores"]
            id_rows_at_iy = cross_section_at_iy["id_row"]
            width_rows_at_iy = cross_section_at_iy["width_row"]
            number_pores_at_iy = cross_section_at_iy["number_of_pores_in_row"]
            number_non_void_cells_in_row_at_iy = cross_section_at_iy[
                                                "number_non_void_cells_in_row"]
            max_height_location_at_iy = 0 # Just initialisation
            i = min(id_rows_at_iy)
            
            if (True not in pores_at_iy.values): # This means there is no holes
                                                 # at this iy section, neither 
                                                # internal nor upper boundaries
                max_height_location_at_iy = z_at_iy[max(id_rows_at_iy)] #AQUI
                height =  max_height_location_at_iy - min(z_at_iy)
                width = max(width_rows_at_iy)
                z_location_max_width = width_rows_at_iy.argmax(width)
                depth = z_at_iy.to_numpy()[z_location_max_width] - min(z_at_iy)
            
            else:
                while (i < max(id_rows_at_iy)):
                    if (pores_at_iy[i]):
                        if (True not in pores_at_row_are_internal[i]): # This 
                                     # means all the pores are upper boundaries
                            max_height_location_at_iy = z_at_iy[i]
                            height =  max_height_location_at_iy - min(z_at_iy)
                            i = max(id_rows_at_iy) # # Break the loop
                    i = i + 1
                
                if (max_height_location_at_iy == 0): # This means the iy 
                                     # section has holes, but they are internal 
                    max_height_location_at_iy = z_at_iy[i-1]
                    height =  max_height_location_at_iy - min(z_at_iy)
                    
                mask2 = (z_at_iy < max_height_location_at_iy)
                possible_max_widths = width_rows_at_iy[mask2]
                try:
                    width = max(possible_max_widths)
                except ValueError as e:
                    print("Error", e)
                location_top_depth_level = np.argmax(possible_max_widths)       
                depth = ((z_at_iy).to_numpy())[location_top_depth_level] - min(
                                                                       z_at_iy)
            
            porous_volume_at_iy = np.sum(number_pores_at_iy.to_numpy()) * (
                                                                  cell_size**3)
            total_volume_material_at_iy = (np.sum(
                               number_non_void_cells_in_row_at_iy.to_numpy()) + 
                        np.sum(number_pores_at_iy.to_numpy())) * (cell_size**3)
            
            porosity_at_iy = porous_volume_at_iy/total_volume_material_at_iy
            
        cross_sections_statistics.append([iy, width, height, depth, 
                                  porosity_at_iy, total_volume_material_at_iy])
               
    cross_sections_statistics_df = pd.DataFrame(cross_sections_statistics, 
                                                columns = ["iy", "width", 
                                                           "height", "depth", 
                                                           "porosity_at_iy", 
                                                "total_volume_material_at_iy"])
    
    results_dir = _measure_results_dir(name_new_folder)
    cross_sections_statistics_df.to_csv(
        results_dir / "cross_sections_statistics.csv",
        index=False,
        encoding="utf-8",
    )

    return cross_sections_statistics_df


def calculate_statistics_rows_meltpool(name_new_folder, CSV_3D, 
                                       laser_radius_test_case_i, 
                                       meltpool_is_continuous, measure_cfg):

    
    # This function takes the .csv file tht represents the meltpool and 
    # calculates several metrics for every row in the meltpool. 
    # The resulting objects are: 
    # 1. Statistics = [id_row, y_coord, z_coord_ x_min, x_max, 
    # row_has_pores, number_of_pores_in_row, width_row, 
    # number_non_void_cells_in_row]
    # 2. pore_locatios_at_rows = A file with "NA" if the row has no pores. 
    # Otherwise, it has list with the x_coord of every pore at the row
    # 3. pores_at_row_are_internal = A file with "NA" if the row has no pores.
    # Otherwise, it has "True" or "False" for every pore in the row. True if 
    # the pore is internal, Flase, otherwise
    

    cell_size = measure_cfg.cell_size


    df = pd.read_csv(CSV_3D)
    analysis_window = _compute_analysis_y_levels(
        df,
        measure_cfg,
        spot_size=2 * laser_radius_test_case_i,
    )
    x = _round_array(df["Points_0"].to_numpy())
    y = analysis_window.y_values
    z = _round_array(df["Points_2"].to_numpy())
    y_merge_tol = analysis_window.y_merge_tol
    
    void_iy_levels= []
    if (not meltpool_is_continuous):
        void_iy_levels = load(str(_measure_aux_dir(name_new_folder) / "void_iy_levels.joblib"))

    id_row = 0
    Statistics = []
    pore_locatios_at_rows = []
    pores_at_row_are_internal = []
    
    # Iterate over all the y-sections
    for iy, iy_actual in zip(
        analysis_window.y_levels,
        analysis_window.y_levels_actual,
    ):
        section_support = _evaluate_section_support(
            y_reported=iy,
            y_actual=iy_actual,
            y_values=y,
            z_values=z,
            y_tol=y_merge_tol,
            cell_size=cell_size,
        )
        if not section_support.is_valid:
            continue
        if not np.any(np.isclose(iy, void_iy_levels)):
            section_geometry = _build_section_geometry(
                df=df,
                y_actual=iy_actual,
                y_values=y,
                y_tol=y_merge_tol,
                cell_size=cell_size,
            )
            cells_at_iy = section_geometry.cells
            x_at_iy = section_geometry.x_values
            y_at_iy = section_geometry.y_values
            z_at_iy = section_geometry.z_values
            z_min_at_iy_that_is_in_original_mesh = section_geometry.z_min_mesh
            z_max_at_iy_that_is_in_original_mesh = section_geometry.z_max_mesh
            x_min_at_iy_that_is_in_original_mesh = section_geometry.x_min_mesh
            x_max_at_iy_that_is_in_original_mesh = section_geometry.x_max_mesh
            
            iz = z_min_at_iy_that_is_in_original_mesh
            
            while (iz <= z_max_at_iy_that_is_in_original_mesh):
                row_evaluation = _evaluate_section_row(
                    cells_at_iy=cells_at_iy,
                    x_at_iy=x_at_iy,
                    z_at_iy=z_at_iy,
                    iz=iz,
                    cell_size=cell_size,
                )
                if row_evaluation is None:
                    iz = z_max_at_iy_that_is_in_original_mesh
                    iz = _round_scalar(iz + cell_size) 
                              
                else:
                    if row_evaluation.n_pores > 0:
                        pore_locations_at_row_i = [id_row, *row_evaluation.pore_locations]
                        pore_locatios_at_rows.append(pore_locations_at_row_i)
                        pores_at_row_i_are_internal = [id_row, *row_evaluation.pores_are_internal]
                        pores_at_row_are_internal.append(
                            pores_at_row_i_are_internal
                        )
                    else:
                        pore_locatios_at_rows.append([id_row, "NA"])
                        pores_at_row_are_internal.append([id_row, "NA"])
                    
                    new_statistics_row = [id_row, iy, iz, 
                                       row_evaluation.x_min_mesh, 
                                       row_evaluation.x_max_mesh, 
                                      row_evaluation.row_has_pores, row_evaluation.n_pores, row_evaluation.width_row,
                                                  row_evaluation.number_non_void_cells]
                    
                    Statistics.append(new_statistics_row)
                    iz = _round_scalar(iz + cell_size)
                    id_row = id_row + 1
            
    row_statistics = pd.DataFrame(Statistics, columns = ["id_row", "y_coord", 
                                                          "z_coord_", "x_min", 
                                                          "x_max", 
                                                          "row_has_pores", 
                                                      "number_of_pores_in_row", 
                                                          "width_row",
                                               "number_non_void_cells_in_row"])
    results_dir = _measure_results_dir(name_new_folder)
    row_statistics.to_csv(
        results_dir / "row_statistics.csv",
        index=False,
        encoding="utf-8",
    )
    
    return row_statistics, pore_locatios_at_rows, pores_at_row_are_internal

def plotResults(name_new_folder, 
                CSV_CROSS_SECTIONS = "./cross_sections_statistics.csv"):
    results_dir = _measure_results_dir(name_new_folder)

    def generate_figure(x, y_values, xlabel, ylabel, title, name_png_file, 
                        results_dir, referenceValue = False):
        plt.figure()
        plt.plot(x, y_values, marker="x") 
        if (referenceValue == False):
            plt.axhline(y=y_values.mean(), color="red", linestyle="--", 
                        label="Mean")
        else:
            plt.axhline(y=y_values.mean(), color="green", linestyle="--", 
                        label="Mean")
            plt.axhline(y=referenceValue, color="red", linestyle="--", 
                        label = str(referenceValue))
        plt.xlabel(xlabel + " (m)")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(results_dir / f"{name_png_file}.png")
    
    df = pd.read_csv(CSV_CROSS_SECTIONS)
    y_locations = df["iy"]
    
    keys_for_plot = ["width", "height", "depth", "porosity_at_iy"]
    
    for key in keys_for_plot:
        values_for_plot = df[key]
        if key == "porosity_at_iy":
            generate_figure(y_locations, values_for_plot, "y_coordinate", 
                            "Porosity (porous volume / total volume)", 
                            "Porosity vs. y-coordinate", "Porosity", 
                            results_dir)
            
        else:
            generate_figure(y_locations, values_for_plot, "y_coordinate", 
                            key + " (m)", key.capitalize() + 
                            " vs. y-coordinate", key.capitalize(), 
                            results_dir)
            
    values_for_plot = df["depth"].to_numpy()/df["width"].to_numpy()
    generate_figure(y_locations, values_for_plot, "y_coordinate", 
                    "D/W","D/W vs. y-coordinate", "DByW", results_dir, 0.5)
            

def calculate_geometry_full_meltpool(name_new_folder, laser_radius_test_case_i,
                                     measure_cfg, CSV_3D="meltpool.csv"):
    df = pd.read_csv(CSV_3D)
    analysis_window = _compute_analysis_y_levels(
        df,
        measure_cfg,
        spot_size=2 * laser_radius_test_case_i,
    )
    _emit_analysis_window_warnings(name_new_folder, measure_cfg, analysis_window)

    meltpool_is_continuous = is_meltpool_continuous(name_new_folder,
                                                    laser_radius_test_case_i,
                                                    measure_cfg, CSV_3D=CSV_3D
                                                    )
    
    if (meltpool_is_continuous):
        row_statistics, pore_locatios_at_rows, \
        pores_at_row_are_internal = calculate_statistics_rows_meltpool(
                                                               name_new_folder,
                                                               CSV_3D,
                                                      laser_radius_test_case_i,
                                                      meltpool_is_continuous, 
                                                      measure_cfg)

        cross_sections_statistics = calculate_cross_sections_statistics(
            name_new_folder,
            row_statistics,
            pore_locatios_at_rows,
            pores_at_row_are_internal,
            meltpool_is_continuous,
            measure_cfg,
        )

        print("Generating profiles for the variables")
        plotResults(name_new_folder, 
       CSV_CROSS_SECTIONS = str(_measure_results_dir(name_new_folder) / "cross_sections_statistics.csv"))
        
    else:
        print("Meltpool is not continuous")
