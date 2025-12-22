from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class Config:
    mesh_density: str
    parameters_file: str
    output_dir: str

def load_config(path: str) -> Config:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    data = yaml.safe_load(p.read_text()) or {}
    return Config(**data)
