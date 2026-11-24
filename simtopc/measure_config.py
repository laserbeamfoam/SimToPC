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
  Definition of the configuration schema used for melt-pool measurement
  in SimToPC.

  This module defines an immutable dataclass that stores the parameters
  controlling the spatial range and resolution used during the
  post-processing and characterisation of melt-pool geometry.

Assumptions
  - All parameters are provided in consistent physical units
  - The configuration values are validated at a higher level in the
    SimToPC workflow

Authors
  Simon A. Rodriguez, University College Dublin (UCD)
  Alojz Ivankovic, University College Dublin (UCD)
  Petar Cosic, University College Dublin (UCD)
  Tom Flint, University of Manchester (UoM)
  Philip Cardiff, University College Dublin (UCD)
"""


from dataclasses import dataclass, field
from typing import Optional

from simtopc.measure.cells import AxesConfig


@dataclass(frozen=True)
class TrimConfig:
    enabled: bool = False
    start_spot_sizes: float = 0.0
    end_spot_sizes: float = 0.0

    def validate(self) -> None:
        if self.start_spot_sizes < 0:
            raise ValueError(
                "measure.trim.start_spot_sizes must be non-negative, "
                f"got {self.start_spot_sizes}."
            )
        if self.end_spot_sizes < 0:
            raise ValueError(
                "measure.trim.end_spot_sizes must be non-negative, "
                f"got {self.end_spot_sizes}."
            )

GEOMETRY_MODES = ("single_track", "metallographic")
WINDOW_MODES = ("fixed", "steady_stretch")
TRACK_REFERENCES = ("case", "laser_start")


@dataclass(frozen=True)
class MeasureConfig:
    y_begin: float
    y_end: float
    x_min: float
    x_max: float
    cell_size: Optional[float]          # None ("auto"): from the blockMeshDict (metallographic mode)
    min_points_per_zrow: int = 4
    extraction_mode: str = "point_fields"
    trim: TrimConfig = field(default_factory=TrimConfig)
    # cell-based modes (cell reader): case axes and final-time fields
    axes: AxesConfig = field(default_factory=AxesConfig)
    melt_field: str = "meltHistory"
    metal_field: str = "alpha.metal"
    geometry_mode: str = "single_track"
    substrate_top: Optional[float] = None
    steady_sections: bool = False
    laser_off_time: Optional[float] = None
    # metallographic mode: width rule, window and track reference (see simtopc.measure.metallographic)
    width_max_rows_down: int = 2
    window_mode: str = "fixed"
    track_reference: str = "case"
    steady_tolerance: float = 5e-6
    steady_filter_length: float = 50e-6
    window_margin: float = 50e-6
    window_length: float = 400e-6
    window_step: float = 50e-6

    def validate(self) -> None:
        if self.y_end <= self.y_begin:
            raise ValueError(
                "measure.y_end must be greater than measure.y_begin, "
                f"got y_begin={self.y_begin} and y_end={self.y_end}."
            )
        if self.x_max < self.x_min:
            raise ValueError(
                "measure.x_max must be greater than or equal to measure.x_min, "
                f"got x_min={self.x_min} and x_max={self.x_max}."
            )
        if self.cell_size is None:
            if self.geometry_mode != "metallographic":
                raise ValueError(
                    "measure.cell_size auto (from the blockMeshDict of each case) is only "
                    "available with measure.geometry_mode metallographic."
                )
        elif self.cell_size <= 0:
            raise ValueError(
                "measure.cell_size must be positive, "
                f"got {self.cell_size}."
            )
        if self.min_points_per_zrow < 1:
            raise ValueError(
                "measure.min_points_per_zrow must be at least 1, "
                f"got {self.min_points_per_zrow}."
            )
        if self.extraction_mode not in {"point_fields", "cell_centres"}:
            raise ValueError(
                "measure.extraction_mode must be 'point_fields' or "
                f"'cell_centres', got {self.extraction_mode!r}."
            )
        self.trim.validate()
        self.axes.validate()
        if self.geometry_mode not in GEOMETRY_MODES:
            raise ValueError(
                "measure.geometry_mode must be one of "
                f"{', '.join(GEOMETRY_MODES)}, got {self.geometry_mode!r}."
            )
        if self.geometry_mode == "single_track" and (
                self.axes.track, self.axes.vertical) != ("y", "z"):
            raise ValueError(
                "measure.geometry_mode single_track measures the point cloud with "
                "the track along y and z vertical (measure.axes {track: y, vertical: z}); "
                "adapt the case with tools/adapt_case_to_simtopc.py, or use "
                "geometry_mode metallographic."
            )
        if not isinstance(self.steady_sections, bool):
            raise ValueError(
                "measure.steady_sections must be true or false, "
                f"got {self.steady_sections!r}."
            )
        if self.steady_sections and self.substrate_top is None:
            raise ValueError(
                "measure.substrate_top (the top of the substrate plate, m) is needed by "
                "measure.steady_sections."
            )
        if self.laser_off_time is not None and self.laser_off_time <= 0:
            raise ValueError(
                f"measure.laser_off_time must be positive, got {self.laser_off_time}."
            )
        if self.geometry_mode == "metallographic" and self.substrate_top is None:
            raise ValueError(
                "measure.substrate_top (the top of the substrate plate, m) is needed by "
                "measure.geometry_mode metallographic."
            )
        if self.window_mode not in WINDOW_MODES:
            raise ValueError(
                f"measure.window_mode must be one of {', '.join(WINDOW_MODES)}, "
                f"got {self.window_mode!r}."
            )
        if self.track_reference not in TRACK_REFERENCES:
            raise ValueError(
                f"measure.track_reference must be one of {', '.join(TRACK_REFERENCES)}, "
                f"got {self.track_reference!r}."
            )
        if self.geometry_mode != "metallographic" and (
                self.window_mode != "fixed" or self.track_reference != "case"):
            raise ValueError(
                "measure.window_mode steady_stretch and measure.track_reference laser_start "
                "are options of measure.geometry_mode metallographic."
            )
        if not isinstance(self.width_max_rows_down, int) or self.width_max_rows_down < 0:
            raise ValueError(
                "measure.width_max_rows_down must be a non-negative integer, "
                f"got {self.width_max_rows_down!r}."
            )
        for key in ("steady_tolerance", "steady_filter_length", "window_margin",
                    "window_length", "window_step"):
            if getattr(self, key) <= 0:
                raise ValueError(f"measure.{key} must be positive, got {getattr(self, key)}.")
        for key in ("melt_field", "metal_field"):
            value = getattr(self, key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"measure.{key} must be a non-empty field name, got {value!r}."
                )
