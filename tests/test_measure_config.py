import pytest

from simtopc.measure_config import MeasureConfig, TrimConfig


def make_valid_measure_config(**overrides):
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


def test_measure_config_accepts_valid_values():
    cfg = make_valid_measure_config()
    cfg.validate()


@pytest.mark.parametrize(
    ("field_name", "value", "expected_message"),
    [
        ("cell_size", -1.0, "measure.cell_size must be positive"),
        ("min_points_per_zrow", 0, "measure.min_points_per_zrow must be at least 1"),
    ],
)
def test_measure_config_rejects_invalid_scalar_values(field_name, value, expected_message):
    cfg = make_valid_measure_config(**{field_name: value})
    with pytest.raises(ValueError, match=expected_message):
        cfg.validate()


def test_measure_config_rejects_invalid_y_window():
    cfg = make_valid_measure_config(y_begin=2.0e-4, y_end=2.0e-4)
    with pytest.raises(ValueError, match="measure.y_end must be greater than measure.y_begin"):
        cfg.validate()


def test_measure_config_rejects_invalid_x_window():
    cfg = make_valid_measure_config(x_min=3.0e-4, x_max=2.0e-4)
    with pytest.raises(ValueError, match="measure.x_max must be greater than or equal to measure.x_min"):
        cfg.validate()


def test_trim_config_rejects_negative_start_trim():
    cfg = make_valid_measure_config(
        trim=TrimConfig(enabled=True, start_spot_sizes=-1.0, end_spot_sizes=0.0)
    )
    with pytest.raises(ValueError, match="measure.trim.start_spot_sizes must be non-negative"):
        cfg.validate()


def test_trim_config_rejects_negative_end_trim():
    cfg = make_valid_measure_config(
        trim=TrimConfig(enabled=True, start_spot_sizes=0.0, end_spot_sizes=-1.0)
    )
    with pytest.raises(ValueError, match="measure.trim.end_spot_sizes must be non-negative"):
        cfg.validate()
