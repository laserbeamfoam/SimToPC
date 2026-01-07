from __future__ import annotations

from pathlib import Path
from simtopc.config import load_config


def run(config_path: str | Path) -> None:
    # 1) Resolve config path
    cfg_path = Path(config_path).expanduser().resolve()
    if not cfg_path.exists():
        raise FileNotFoundError(cfg_path)

    # 2) Import TF only when running surrogate (optional dependency)
    try:
        import tensorflow as _tf  # noqa: F401
    except Exception as e:
        raise RuntimeError(
            "TensorFlow is required for 'simtopc surrogate'. "
            "Install it (e.g. pip install tensorflow) and try again."
        ) from e

    # 3) Load config
    cfg_all = load_config(str(cfg_path))

    # 4) Call implementation
    from simtopc.surrogate.impl import train_from_config
    train_from_config(cfg_all=cfg_all, config_path=cfg_path)
