from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any
import yaml


@dataclass
class SurrogateConfig:
    seed: int = 123
    n_epochs: int = 200
    n_divisions_for_prediction: int = 40
    possible_outputs: List[str] = field(default_factory=lambda: [
        "W_mean", "W_std", "D_mean", "D_std", "H_mean", "H_std", "porosity_mean", "porosity_std"
    ])


@dataclass
class Config:
    mesh_density: str
    parameters_file: str
    output_dir: str
    running_on: str
    measure: Dict[str, Any] = field(default_factory=dict)
    surrogate: SurrogateConfig = field(default_factory=SurrogateConfig)


def _resolve_path(base_dir: Path, maybe_path: str) -> str:
    """Resolve a path string relative to base_dir unless it's already absolute."""
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

    return Config(
        mesh_density=_resolve_path(base_dir, mesh_density),
        parameters_file=_resolve_path(base_dir, parameters_file),
        output_dir=_resolve_path(base_dir, output_dir),
        running_on=data["running_on"],
        measure=data.get("measure", {}) or {},
        surrogate=surrogate,
    )
