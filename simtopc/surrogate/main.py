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
  Entry point for the surrogate-modelling stage of the SimToPC workflow.

  This module performs minimal validation of the user configuration
  and dispatches execution to the surrogate-model implementation.

Assumptions
  - This module is invoked via the SimToPC command-line interface
  - TensorFlow is available in the execution environment
  - A valid SimToPC configuration file is provided

Authors
  Simon A. Rodriguez, University College Dublin (UCD)
  Alojz Ivankovic, University College Dublin (UCD)
  Petar Cosic, University College Dublin (UCD)
  Tom Flint, University of Manchester (UoM)
  Philip Cardiff, University College Dublin (UCD)
"""


from pathlib import Path

def run(config_path: str) -> None:
    cfg_path = Path(config_path).expanduser().resolve()
    if not cfg_path.exists():
        raise FileNotFoundError(cfg_path)

    # TF only needed for surrogate
    try:
        import tensorflow as _tf  # noqa: F401
    except Exception as e:
        raise RuntimeError(
            "TensorFlow is required for 'simtopc surrogate'. "
            "Install it (e.g. pip install tensorflow) and try again."
        ) from e

    from simtopc.surrogate.impl import run_surrogate
    run_surrogate(str(cfg_path))
