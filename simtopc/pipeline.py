from __future__ import annotations
import subprocess
from pathlib import Path
from simtopc.config import load_config
import sys


def run(config_path: str) -> None:
    cfg = load_config(config_path)
    Path(cfg.output_dir).mkdir(parents=True, exist_ok=True)
    subprocess.run(["python", "measure_W_H_D.py", config_path], check=True)

def surrogate(config_path: str) -> None:
    cfg_path = Path(config_path).expanduser().resolve()
    if not cfg_path.exists():
        raise FileNotFoundError(cfg_path)

    try:
        import tensorflow 
    except ModuleNotFoundError:
        raise SystemExit(
            "TensorFlow no está instalado. Para usar el surrogate instala con:\n"
            "  pip install -e '.[ml]'"
        )

    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "create_and_train_surrogate_model.py"
    if not script.exists():
        raise FileNotFoundError(f"No encuentro el script: {script}")

    subprocess.run(
        [sys.executable, str(script), str(cfg_path)],
        check=True,
        cwd=str(repo_root),
    )


def generate(config_path: str) -> None:
    from simtopc.generate import run_generate
    run_generate(config_path)


