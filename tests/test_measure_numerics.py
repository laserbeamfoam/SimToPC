import numpy as np
import pandas as pd
import pytest

from simtopc.measure.legacy_funcs import (
    _compute_analysis_y_levels,
    _snap_value_to_global_mesh,
)
from simtopc.measure_config import MeasureConfig, TrimConfig


def make_measure_config(**overrides):
    data = {
        "y_begin": 1.0e-4,
        "y_end": 7.0e-4,
        "x_min": 0.0,
        "x_max": 2.0e-4,
        "cell_size": 5.0e-6,
        "min_points_per_zrow": 4,
        "trim": TrimConfig(),
    }
    data.update(overrides)
    return MeasureConfig(**data)


def make_synthetic_meltpool_df(y_levels):
    rows = []
    canonical_x = 1.0e-4
    z_levels = [0.0, 5.0e-6, 1.0e-5, 1.5e-5]
    for y in y_levels:
        for z in z_levels:
            rows.append(
                {
                    "Points_0": canonical_x,
                    "Points_1": y,
                    "Points_2": z,
                }
            )
    return pd.DataFrame(rows)


def test_snap_value_to_global_mesh_rounds_in_expected_directions():
    cell_size = 5.0e-6
    assert _snap_value_to_global_mesh(137.5e-6, cell_size, "forward") == pytest.approx(140.0e-6)
    assert _snap_value_to_global_mesh(662.5e-6, cell_size, "backward") == pytest.approx(660.0e-6)


def test_compute_analysis_y_levels_aligns_reported_window_to_mesh():
    df = make_synthetic_meltpool_df([125.0e-6, 130.0e-6, 675.0e-6])
    measure_cfg = make_measure_config()

    analysis_window = _compute_analysis_y_levels(df, measure_cfg, spot_size=100.0e-6)

    assert analysis_window.y_effective_begin == pytest.approx(125.0e-6)
    assert analysis_window.y_effective_end == pytest.approx(675.0e-6)
    assert analysis_window.y_levels[0] == pytest.approx(125.0e-6)
    assert analysis_window.y_levels[-1] == pytest.approx(675.0e-6)
    assert analysis_window.nominal_mismatch is True


def test_compute_analysis_y_levels_reports_trim_snapping_when_needed():
    df = make_synthetic_meltpool_df(np.arange(100.0e-6, 700.1e-6, 5.0e-6))
    measure_cfg = make_measure_config(
        trim=TrimConfig(enabled=True, start_spot_sizes=1.0, end_spot_sizes=1.0)
    )

    analysis_window = _compute_analysis_y_levels(df, measure_cfg, spot_size=77.0e-6)

    assert analysis_window.trim_snapped is True
    assert analysis_window.y_trimmed_begin_physical == pytest.approx(177.0e-6)
    assert analysis_window.y_trimmed_end_physical == pytest.approx(623.0e-6)
    assert analysis_window.y_levels[0] == pytest.approx(180.0e-6)
    assert analysis_window.y_levels[-1] == pytest.approx(620.0e-6)


def test_compute_analysis_y_levels_applies_trim_to_requested_window_before_observed_window():
    df = make_synthetic_meltpool_df(np.arange(100.0e-6, 685.1e-6, 5.0e-6))
    measure_cfg = make_measure_config(
        trim=TrimConfig(enabled=True, start_spot_sizes=0.5, end_spot_sizes=0.5)
    )

    analysis_window = _compute_analysis_y_levels(df, measure_cfg, spot_size=75.0e-6)

    assert analysis_window.y_trimmed_begin_physical == pytest.approx(137.5e-6)
    assert analysis_window.y_trimmed_end_physical == pytest.approx(662.5e-6)
    assert analysis_window.y_levels[0] == pytest.approx(140.0e-6)
    assert analysis_window.y_levels[-1] == pytest.approx(660.0e-6)


def test_compute_analysis_y_levels_rejects_non_overlapping_window():
    df = make_synthetic_meltpool_df(np.arange(125.0e-6, 676.0e-6, 5.0e-6))
    measure_cfg = make_measure_config(y_begin=8.0e-4, y_end=9.0e-4)

    with pytest.raises(ValueError, match="does not overlap with the observed meltpool window"):
        _compute_analysis_y_levels(df, measure_cfg, spot_size=100.0e-6)


def test_compute_analysis_y_levels_rejects_excessive_trimming():
    df = make_synthetic_meltpool_df(np.arange(125.0e-6, 676.0e-6, 5.0e-6))
    measure_cfg = make_measure_config(
        trim=TrimConfig(enabled=True, start_spot_sizes=3.0, end_spot_sizes=3.0)
    )

    with pytest.raises(ValueError, match="Requested trimming removes the full requested track window"):
        _compute_analysis_y_levels(df, measure_cfg, spot_size=100.0e-6)
