import pytest

from simtopc.measure.main import (
    _coerce_float,
    _coerce_int,
    _require_measure_mapping,
)


def test_require_measure_mapping_rejects_missing_block():
    with pytest.raises(ValueError, match="Missing required 'measure' configuration block"):
        _require_measure_mapping({})


def test_require_measure_mapping_rejects_non_mapping():
    with pytest.raises(ValueError, match="must be a mapping"):
        _require_measure_mapping("bad")


def test_require_measure_mapping_rejects_missing_required_keys():
    with pytest.raises(ValueError, match="measure.y_end"):
        _require_measure_mapping({"y_begin": 1.0e-4})


def test_coerce_float_rejects_non_numeric_value():
    with pytest.raises(ValueError, match="measure.y_begin must be numeric"):
        _coerce_float({"y_begin": "abc"}, "y_begin")


def test_coerce_int_rejects_non_integer_value():
    with pytest.raises(ValueError, match="measure.min_points_per_zrow must be an integer"):
        _coerce_int({"min_points_per_zrow": "abc"}, "min_points_per_zrow", 4)
