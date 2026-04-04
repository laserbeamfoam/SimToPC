from pathlib import Path

import pandas as pd
from joblib import load

from simtopc.measure.legacy_funcs import is_meltpool_continuous
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


def write_meltpool_csv(path: Path, rows):
    df = pd.DataFrame(rows, columns=["Points_0", "Points_1", "Points_2"])
    df.to_csv(path, index=False)


def build_continuous_rows(y_levels, x_value=1.0e-4):
    rows = []
    z_levels = [0.0, 5.0e-6, 1.0e-5, 1.5e-5]
    for y in y_levels:
        for z in z_levels:
            rows.append((x_value, y, z))
    return rows


def test_is_meltpool_continuous_returns_true_for_simple_continuous_case(tmp_path):
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    csv_path = case_dir / "meltpool.csv"
    y_levels = [125.0e-6, 130.0e-6, 135.0e-6, 140.0e-6]
    write_meltpool_csv(csv_path, build_continuous_rows(y_levels))

    measure_cfg = make_measure_config(y_begin=125.0e-6, y_end=140.0e-6)

    result = is_meltpool_continuous(
        str(case_dir),
        laser_radius_test_case_i=50.0e-6,
        measure_cfg=measure_cfg,
        CSV_3D=str(csv_path),
    )

    assert result is True
    assert load(case_dir / "continuous.joblib") is True


def test_is_meltpool_continuous_returns_false_when_a_section_is_missing(tmp_path):
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    csv_path = case_dir / "meltpool.csv"
    y_levels = [125.0e-6, 130.0e-6, 140.0e-6]
    write_meltpool_csv(csv_path, build_continuous_rows(y_levels))

    measure_cfg = make_measure_config(y_begin=125.0e-6, y_end=140.0e-6)

    result = is_meltpool_continuous(
        str(case_dir),
        laser_radius_test_case_i=50.0e-6,
        measure_cfg=measure_cfg,
        CSV_3D=str(csv_path),
    )

    assert result is False
    assert load(case_dir / "continuous.joblib") is False
    assert 135.0e-6 in load(case_dir / "void_iy_levels.joblib")


def test_is_meltpool_continuous_ignores_spurious_y_level_without_support(tmp_path):
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    csv_path = case_dir / "meltpool.csv"
    rows = build_continuous_rows([125.0e-6, 130.0e-6, 135.0e-6, 140.0e-6])
    rows.append((1.0e-4, 211.13e-6, 0.0))
    write_meltpool_csv(csv_path, rows)

    measure_cfg = make_measure_config(y_begin=125.0e-6, y_end=140.0e-6)

    result = is_meltpool_continuous(
        str(case_dir),
        laser_radius_test_case_i=50.0e-6,
        measure_cfg=measure_cfg,
        CSV_3D=str(csv_path),
    )

    assert result is True
    assert load(case_dir / "continuous.joblib") is True
