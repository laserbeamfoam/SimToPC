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


def load_config(path: str) -> Config:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)

    data = yaml.safe_load(p.read_text()) or {}

    # Convert nested dict -> SurrogateConfig
    sur_data = data.get("surrogate", {}) or {}
    surrogate = SurrogateConfig(**sur_data)

    return Config(
        mesh_density=data["mesh_density"],
        parameters_file=data.get("parameters_file", "./parameters.txt"),
        output_dir=data["output_dir"],
        running_on=data["running_on"],
        measure=data.get("measure", {}) or {},
        surrogate=surrogate,
    )
