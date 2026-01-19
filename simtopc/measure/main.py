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
from simtopc.measure_config import MeasureConfig
from simtopc.measure.impl import run_measure_cases


def run(config_path: str | Path) -> None:
    config_path = Path(config_path).resolve()
    cfg_all = load_config(str(config_path))

    m = cfg_all.measure
    measure_cfg = MeasureConfig(
        y_begin=float(m["y_begin"]),
        y_end=float(m["y_end"]),
        x_min=float(m["x_min"]),
        x_max=float(m["x_max"]),
        cell_size=float(m["cell_size"]),
        min_points_per_zrow=int(m.get("min_points_per_zrow", 4)),
    )

    run_measure_cases(cfg_all=cfg_all, measure_cfg=measure_cfg, config_path=config_path)
