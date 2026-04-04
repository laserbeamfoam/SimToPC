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


@dataclass(frozen=True)
class TrimConfig:
    enabled: bool = False
    start_spot_sizes: float = 0.0
    end_spot_sizes: float = 0.0

@dataclass(frozen=True)
class MeasureConfig:
    y_begin: float
    y_end: float
    x_min: float
    x_max: float
    cell_size: float
    min_points_per_zrow: int = 4
    trim: TrimConfig = field(default_factory=TrimConfig)
