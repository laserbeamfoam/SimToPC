from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass
class Config:
    mesh_density: str
    parameters_file: str
    output_dir: str
    running_on: str
    measure: dict = field(default_factory=dict)

def load_config(path: str) -> Config:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    data = yaml.safe_load(p.read_text()) or {}
    return Config(**data)
