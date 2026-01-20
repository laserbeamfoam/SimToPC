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
  Configuration schema and loader utilities for SimToPC.

  This module defines typed configuration objects (dataclasses) used by
  the SimToPC workflow, and provides a YAML loader that:
  - reads a user-supplied config file,
  - applies defaults where appropriate,
  - resolves relative paths with respect to the config file location.

Assumptions
  - The configuration file is a YAML document following the SimToPC schema
  - Paths in the YAML file may be absolute or relative to the config file
  - YAML parsing is performed with yaml.safe_load

Authors
  Simon A. Rodriguez, University College Dublin (UCD)
  Alojz Ivankovic, University College Dublin (UCD)
  Petar Cosic, University College Dublin (UCD)
  Tom Flint, University of Manchester (UoM)
  Philip Cardiff, University College Dublin (UCD)
"""


from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml


@dataclass
class EnvironmentConfig:
    hostname: str = ""
    run_address: str = ""
    of_location: str = ""


@dataclass
class SurrogateConfig:
    seed: int = 123
    n_epochs: int = 200
    n_divisions_for_prediction: int = 40
    possible_outputs: List[str] = field(default_factory=lambda: [
        "W_mean", "W_std", "D_mean", "D_std", "H_mean", "H_std", 
        "porosity_mean", "porosity_std"
    ])


@dataclass
class Config:
    mesh_density: str
    parameters_file: str
    output_dir: str
    running_on: str
    environment: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    measure: Dict[str, Any] = field(default_factory=dict)
    surrogate: SurrogateConfig = field(default_factory=SurrogateConfig)


def _resolve_path(base_dir: Path, maybe_path: str) -> str:
    """Resolve path relative to base_dir if not absolute."""
    if maybe_path is None:
        return maybe_path
    p = Path(maybe_path)
    if p.is_absolute():
        return str(p)
    return str((base_dir / p).resolve())


def load_config(path: str) -> Config:
    config_path = Path(path).expanduser().resolve()
    if not config_path.exists():
        raise FileNotFoundError(config_path)

    base_dir = config_path.parent
    data = yaml.safe_load(config_path.read_text()) or {}

    sur_data = data.get("surrogate", {}) or {}
    surrogate = SurrogateConfig(**sur_data)

    mesh_density = data["mesh_density"]
    parameters_file = data.get("parameters_file", "./parameters.txt")
    output_dir = data["output_dir"]

    env_data = data.get("environment", {}) or {}
    environment = EnvironmentConfig(**env_data)

    return Config(
        mesh_density=_resolve_path(base_dir, mesh_density),
        parameters_file=_resolve_path(base_dir, parameters_file),
        output_dir=_resolve_path(base_dir, output_dir),
        running_on=data["running_on"],
        environment=environment,
        measure=data.get("measure", {}) or {},
        surrogate=surrogate,
    )

    
