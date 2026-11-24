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
  Entry point for the measurement stage of the SimToPC workflow.

  This module parses measurement-related configuration parameters,
  constructs the corresponding configuration object, and invokes
  the core measurement routines responsible for extracting geometric
  and porosity metrics from completed simulation cases.

Assumptions
  - This module is invoked via the SimToPC command-line interface
  - A valid SimToPC configuration file is provided
  - Simulation cases have already been generated and executed
  - Measurement parameters follow the documented SimToPC schema

Authors
  Simon A. Rodriguez, University College Dublin (UCD)
  Alojz Ivankovic, University College Dublin (UCD)
  Petar Cosic, University College Dublin (UCD)
  Tom Flint, University of Manchester (UoM)
  Philip Cardiff, University College Dublin (UCD)
"""


from __future__ import annotations
from pathlib import Path
from simtopc.config import load_config
from simtopc.measure_config import MeasureConfig, TrimConfig
from simtopc.measure.cells import AxesConfig
from simtopc.measure.impl import run_measure_cases


REQUIRED_MEASURE_KEYS = ("y_begin", "y_end", "x_min", "x_max", "cell_size")


def _require_measure_mapping(measure_raw):
    if not measure_raw:
        raise ValueError(
            "Missing required 'measure' configuration block."
        )
    if not isinstance(measure_raw, dict):
        raise ValueError(
            "The 'measure' configuration block must be a mapping of keys to values."
        )
    missing = [key for key in REQUIRED_MEASURE_KEYS if key not in measure_raw]
    if missing:
        missing_list = ", ".join(f"measure.{key}" for key in missing)
        raise ValueError(
            f"Missing required measurement configuration values: {missing_list}."
        )
    return measure_raw


def _coerce_float(mapping, key):
    try:
        return float(mapping[key])
    except (TypeError, ValueError):
        raise ValueError(
            f"measure.{key} must be numeric, got {mapping[key]!r}."
        ) from None


def _coerce_int(mapping, key, default):
    raw_value = mapping.get(key, default)
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        raise ValueError(
            f"measure.{key} must be an integer, got {raw_value!r}."
        ) from None


def _parse_axes(measure_raw):
    axes_raw = measure_raw.get("axes", {}) or {}
    if not isinstance(axes_raw, dict):
        raise ValueError(
            "measure.axes must be a mapping such as {track: y, vertical: z}."
        )
    unknown = set(axes_raw) - {"track", "vertical"}
    if unknown:
        raise ValueError(
            "measure.axes accepts only the keys track and vertical, got "
            + ", ".join(sorted(map(str, unknown))) + "."
        )
    return AxesConfig(
        track=str(axes_raw.get("track", "y")).strip().lower(),
        vertical=str(axes_raw.get("vertical", "z")).strip().lower(),
    )


def _coerce_optional_float(mapping, key):
    if mapping.get(key) is None:
        return None
    return _coerce_float(mapping, key)


def _coerce_choice(mapping, key, default):
    return str(mapping.get(key, default)).strip()


def build_measure_config(m) -> MeasureConfig:
    """MeasureConfig from the 'measure' block of the configuration file (validated)."""
    m = _require_measure_mapping(m)
    trim_raw = m.get("trim", {}) or {}
    if not isinstance(trim_raw, dict):
        raise ValueError("measure.trim must be a mapping of trim options.")
    measure_cfg = MeasureConfig(
        y_begin=_coerce_float(m, "y_begin"),
        y_end=_coerce_float(m, "y_end"),
        x_min=_coerce_float(m, "x_min"),
        x_max=_coerce_float(m, "x_max"),
        cell_size=None if str(m["cell_size"]).strip().lower() == "auto"
        else _coerce_float(m, "cell_size"),
        min_points_per_zrow=_coerce_int(m, "min_points_per_zrow", 4),
        extraction_mode=str(m.get("extraction_mode", "point_fields")),
        trim=TrimConfig(
            enabled=bool(trim_raw.get("enabled", False)),
            start_spot_sizes=_coerce_float(trim_raw, "start_spot_sizes")
            if "start_spot_sizes" in trim_raw else 0.0,
            end_spot_sizes=_coerce_float(trim_raw, "end_spot_sizes")
            if "end_spot_sizes" in trim_raw else 0.0,
        ),
        axes=_parse_axes(m),
        melt_field=str(m.get("melt_field", "meltHistory")),
        metal_field=str(m.get("metal_field", "alpha.metal")),
        geometry_mode=_coerce_choice(m, "geometry_mode", "single_track"),
        substrate_top=_coerce_optional_float(m, "substrate_top"),
        steady_sections=m.get("steady_sections", False),
        laser_off_time=_coerce_optional_float(m, "laser_off_time"),
        width_max_rows_down=_coerce_int(m, "width_max_rows_down", 2),
        window_mode=_coerce_choice(m, "window_mode", "fixed"),
        track_reference=_coerce_choice(m, "track_reference", "case"),
        steady_tolerance=_coerce_float(m, "steady_tolerance") if "steady_tolerance" in m else 5e-6,
        steady_filter_length=_coerce_float(m, "steady_filter_length")
        if "steady_filter_length" in m else 50e-6,
        window_margin=_coerce_float(m, "window_margin") if "window_margin" in m else 50e-6,
        window_length=_coerce_float(m, "window_length") if "window_length" in m else 400e-6,
        window_step=_coerce_float(m, "window_step") if "window_step" in m else 50e-6,
    )
    measure_cfg.validate()
    return measure_cfg


def run(config_path: str | Path) -> None:
    config_path = Path(config_path).resolve()
    cfg_all = load_config(str(config_path))

    measure_cfg = build_measure_config(cfg_all.measure)

    run_measure_cases(cfg_all=cfg_all, measure_cfg=measure_cfg, 
    config_path=config_path)
