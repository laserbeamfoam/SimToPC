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
