from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from simtopc.measure.legacy_funcs import (
    calculate_cross_sections_statistics,
    calculate_statistics_rows_meltpool,
    is_meltpool_continuous,
)
from simtopc.measure_config import MeasureConfig, TrimConfig


CELL_SIZE = 1.0e-6
Y_LEVELS = [0.0, 1.0e-6, 2.0e-6, 3.0e-6]


def make_measure_config(**overrides):
    data = {
        "y_begin": 0.0,
        "y_end": 3.0e-6,
        "x_min": 0.0,
        "x_max": 4.0e-6,
        "cell_size": CELL_SIZE,
        "min_points_per_zrow": 3,
        "trim": TrimConfig(),
    }
    data.update(overrides)
    return MeasureConfig(**data)


def write_meltpool_csv(path: Path, rows):
    df = pd.DataFrame(rows, columns=["Points_0", "Points_1", "Points_2"])
    df.to_csv(path, index=False)


def build_diamond_sections(include_internal_missing_cell=False):
    rows = []
    for y in Y_LEVELS:
        for x in [1.0e-6, 2.0e-6, 3.0e-6]:
            rows.append((x, y, 0.0))

        middle_row_x = [0.0, 1.0e-6, 2.0e-6, 3.0e-6, 4.0e-6]
        if include_internal_missing_cell:
            middle_row_x.remove(2.0e-6)
        for x in middle_row_x:
            rows.append((x, y, 1.0e-6))

        for x in [1.0e-6, 2.0e-6, 3.0e-6]:
            rows.append((x, y, 2.0e-6))
    return rows


def run_controlled_measurement(tmp_path, rows, measure_cfg):
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    csv_path = case_dir / "meltpool.csv"
    write_meltpool_csv(csv_path, rows)

    is_continuous = is_meltpool_continuous(
        str(case_dir),
        laser_radius_test_case_i=0.5e-6,
        measure_cfg=measure_cfg,
        CSV_3D=str(csv_path),
    )
    row_statistics, pore_locations, pores_are_internal = (
        calculate_statistics_rows_meltpool(
            str(case_dir),
            str(csv_path),
            laser_radius_test_case_i=0.5e-6,
            meltpool_is_continuous=is_continuous,
            measure_cfg=measure_cfg,
        )
    )
    cross_sections = calculate_cross_sections_statistics(
        str(case_dir),
        row_statistics,
        pore_locations,
        pores_are_internal,
        is_continuous,
        measure_cfg,
    )
    return is_continuous, row_statistics, pore_locations, pores_are_internal, cross_sections


def test_controlled_no_void_geometry_recovers_expected_section_metrics(tmp_path):
    measure_cfg = make_measure_config()

    is_continuous, row_statistics, _, _, cross_sections = run_controlled_measurement(
        tmp_path,
        build_diamond_sections(include_internal_missing_cell=False),
        measure_cfg,
    )

    assert is_continuous is True
    assert len(cross_sections) == len(Y_LEVELS)
    assert np.allclose(cross_sections["width"], 4.0e-6)
    assert np.allclose(cross_sections["height"], 2.0e-6)
    assert np.allclose(cross_sections["depth"], 1.0e-6)
    assert np.allclose(cross_sections["porosity_at_iy"], 0.0)

    middle_rows = row_statistics[np.isclose(row_statistics["z_coord_"], 1.0e-6)]
    assert np.allclose(middle_rows["width_row"], 4.0e-6)
    assert (middle_rows["number_non_void_cells_in_row"] == 4).all()


def test_controlled_internal_missing_cell_is_reported_in_rows_and_void_fraction(tmp_path):
    measure_cfg = make_measure_config(min_points_per_zrow=2)

    is_continuous, row_statistics, pore_locations, pores_are_internal, cross_sections = (
        run_controlled_measurement(
            tmp_path,
            build_diamond_sections(include_internal_missing_cell=True),
            measure_cfg,
        )
    )

    assert is_continuous is True
    assert np.allclose(cross_sections["width"], 4.0e-6)
    assert np.allclose(cross_sections["height"], 2.0e-6)
    assert np.allclose(cross_sections["depth"], 1.0e-6)
    assert np.allclose(cross_sections["porosity_at_iy"], 0.125)

    missing_cell_rows = row_statistics[row_statistics["row_has_pores"]]
    assert len(missing_cell_rows) == len(Y_LEVELS)
    assert (missing_cell_rows["number_of_pores_in_row"] == 1).all()
    assert (missing_cell_rows["number_non_void_cells_in_row"] == 3).all()
    assert np.allclose(missing_cell_rows["width_row"], 4.0e-6)

    assert [entry[1] for entry in pore_locations if entry[1] != "NA"] == pytest.approx(
        [2.0e-6] * len(Y_LEVELS)
    )
    assert [entry[1] for entry in pores_are_internal if entry[1] != "NA"] == [
        True
    ] * len(Y_LEVELS)
