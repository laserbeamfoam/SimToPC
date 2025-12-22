from __future__ import annotations
import subprocess
from pathlib import Path
from simtopc.config import load_config

def run(config_path: str) -> None:
    cfg = load_config(config_path)
    Path(cfg.output_dir).mkdir(parents=True, exist_ok=True)

    # TODO: reemplaza estos nombres por tus scripts reales
    #subprocess.run(["python", "generate_data.py"], check=True)
    subprocess.run(["python", "measure_W_H_D.py"], check=True)


def surrogate(config_path: str) -> None:
    # (Opcional) validar que el config existe; si ya lo haces en otra parte, perfecto.
    cfg_path = Path(config_path)
    if not cfg_path.exists():
        raise FileNotFoundError(cfg_path)

    # Chequeo “amable” de TensorFlow (solo para este comando)
    try:
        import tensorflow  # noqa: F401
    except ModuleNotFoundError:
        raise SystemExit(
            "TensorFlow no está instalado. Para usar el surrogate instala con:\n"
            "  pip install -e '.[ml]'"
        )

    # Ejecutar el script desde la raíz del repo aunque el usuario llame simtopc desde otro directorio
    repo_root = Path(__file__).resolve().parents[1]  # .../SimToPC/
    script = repo_root / "create_and_train_surrogate_model.py"
    if not script.exists():
        raise FileNotFoundError(f"No encuentro el script: {script}")

    subprocess.run(["python", str(script)], check=True, cwd=str(repo_root))


def generate(config_path: str) -> None:
    from pathlib import Path
    import subprocess

    cfg_path = Path(config_path)
    if not cfg_path.exists():
        raise FileNotFoundError(cfg_path)

    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "generate_data.py"

    if not script.exists():
        raise FileNotFoundError(f"No encuentro el script: {script}")

    subprocess.run(
        ["python", str(script)],
        check=True,
        cwd=str(repo_root),
    )
